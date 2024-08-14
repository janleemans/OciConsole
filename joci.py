# joci: a command-line interface for managing your OCI environment: listing available entities, 
# starting and stopping entities, all without the need to use OCID's or repeated authentication
# This script will NOT create new or delete any entities, as in that case a lot of info needs to be provided, use the GUI for that.

import oci
import readchar

# Make sure to configure the .oci/config file as proposed during the creation of an API key for your oci user.
# Also pick the right profile in case you have multiple profiles in your config file, using the name of the profile as below
config = oci.config.from_file("~/.oci/config", "DEFAULT")

# Validate Authentication
#------------------------
idd = oci.identity.IdentityClient(config)
identity = oci.identity.IdentityClient(config)
user = identity.get_user(config["user"]).data
tenancy = identity.get_tenancy(config["tenancy"]).data
DEBUG = True

# You can add an entry "compartment" to your OCI config file to set your default string compartment for the script.  
try:
    compart = config["compartment"]
except:
    # if not provided, use the root compartment of the user
    compart = user.compartment_id

# Extract the compartment name
compartment_response = identity.get_compartment(compartment_id=compart).data
compartment_name = compartment_response.name

# Main top level loop showing available commands
while (True):
    print('----------------------------------------')
    print ("  - Instance   : ", tenancy.description)
    print ("  - Compartment: ", compartment_name)
    print ("  - Username   : ", user.name)
    print('--------------')
    print("Actions:")
    print("g: Go to a different compartment")
    print("c: Compute instances: list, start or stop")
    print("n: Networks: list available VCN's")
    print("s: Storage")
    print("d: Databases - only autonomous for now")
    print("i: CN objects: containers")
    print("q: quit")
    action = readchar.readchar()

# Change the current compartment (up or down)
    if (action =='g'):
        list_compartments_response = identity.list_compartments(
            compartment_id=compart)
        compartment_list = list_compartments_response.data
        root_compartment = identity.get_compartment(compartment_id=compart).data
        if DEBUG: print (root_compartment)
        if (root_compartment.compartment_id is not None ):
            parent_compartment = identity.get_compartment(compartment_id=root_compartment.compartment_id).data
            #print (parent_compartment)
            compartment_list.append(parent_compartment)
        print('----------------------------------------')
        print ("Available compartments:")
        for cnt, compartment in enumerate(compartment_list):
            print("Compartment ",cnt,": ",compartment.name)

        try:
            index = int(input("Enter compartment ID to go to: "))
            if index >= 0 and index < len(compartment_list):
                print ("Going to compartment: ",compartment_list[index].name)
                compartment_name = compartment_list[index].name
                compart = compartment_list[index].id
            else:
                print("Not a compartment number")
        except Exception as e:
            print(f"An error occurred: {e}")

    # Manage Compute instances
    elif (action == 'c'):
        compute_client = oci.core.ComputeClient(config)
        network_client = oci.core.VirtualNetworkClient(config)

        while (action != '-'):
            instances = compute_client.list_instances(compartment_id=compart).data
            if DEBUG: print(instances)
            print('----------------------------------------')
            print ("Instances:")
            for cnt, i in enumerate(instances):
                public_ip = 'None'
                if (i.lifecycle_state !='TERMINATED'): #terminated instances don't have VNC's so they need to be excluded here
                    vnic_attachments = compute_client.list_vnic_attachments(
                        compartment_id=compart, instance_id=i.id).data
                    if DEBUG: print (vnic_attachments)
                    vnics = [network_client.get_vnic(va.vnic_id).data for va in vnic_attachments]
                    if DEBUG: print (vnics)
                    primary_vnic_attachment = next(va for va in vnics if va.is_primary)
                    vnic = network_client.get_vnic(primary_vnic_attachment.id).data
                    # Get the IP address of the instance so you can ssh into it easily
                    public_ip = vnic.public_ip

                print("Instance ",cnt, ': ', i.lifecycle_state,", Name: ", i.display_name, ", IP=",public_ip)

            print('----------------------------------------')
            print("Instance Actions:\n u: bring an instance UP \n d: bring an instance DOWN \n a: print all attributes \n space: re-list instances \n -: back to main menu")
            action = readchar.readchar()

            # Start an instance - bring it Up
            if (action == 'u'):
                try:
                    index = int(input("Enter Instance ID to start: "))
                    if index >= 0 and index < len(instances):
                        print ("Starting instance: ",instances[index].display_name)
                        my_response = compute_client.instance_action(instances[index].id, 'START')
                        print('--> response: ',my_response.data.lifecycle_state)
                    else:
                        print("Not an instance number")
                except Exception as e:
                    print(f"An error occurred: {e}")

            # Stop an instance - bring it Down
            elif (action == 'd'):
                try:
                    index = int(input("Enter Instance ID to stop: "))
                    if index >= 0 and index < len(instances):
                        print ("Stopping instance: ",instances[index].display_name)
                        my_response = compute_client.instance_action(instances[index].id, 'SOFTSTOP')
                        print('--> response: ',my_response.data.lifecycle_state)
                    else:
                        print("Not an instance number")
                except Exception as e:
                    print(f"An error occurred: {e}")

            # Print all the details of a specific instance
            elif(action =='a'):
                try:
                    index = int(input("Enter Instance ID to list: "))
                    if index >= 0 and index < len(instances):
                        print("Instance details: ",instances[index])
                    else:
                        print("Not an instance number")
                except Exception as e:
                    print(f"An error occurred: {e}")

            # Quit immediately
            elif (action == 'q'):
                print("Quitting")
                quit()

    elif(action =='d'):
        database_client = oci.database.DatabaseClient(config)
        while (action != '-'):
            autonomous_databases = database_client.list_autonomous_databases(compart).data
            print('----------------------------------------')
            print ("Databases:")
            for cnt, adb in enumerate(autonomous_databases):
                print(f"DB {cnt}: {adb.display_name}, Created on {adb.time_created}, State: {adb.lifecycle_state}")

            print('----------------------------------------')
            print("DB Actions:\n u: bring an instance UP \n d: bring an instance DOWN \n space: re-list instances \n -: back to main menu")
            action = readchar.readchar()

            # Start an instance - bring it Up
            if (action == 'u'):
                try:
                    index = int(input("Enter Instance ID to start: "))
                    if index >= 0 and index < len(autonomous_databases):
                        print ("Starting instance: ",autonomous_databases[index].display_name)
                        response = database_client.start_autonomous_database(autonomous_databases[index].id)
                        print('--> response: ',response.status)
                    else:
                        print("Not an instance number")
                except Exception as e:
                    print(f"An error occurred: {e}")

            # Stop an instance - bring it Down
            elif (action == 'd'):
                try:
                    index = int(input("Enter Instance ID to stop: "))
                    if index >= 0 and index < len(autonomous_databases):
                        print ("Stopping instance: ",autonomous_databases[index].display_name)
                        response = database_client.stop_autonomous_database(autonomous_databases[index].id)
                        print('--> response: ',response.status)
                    else:
                        print("Not an instance number")
                except Exception as e:
                    print(f"An error occurred: {e}")

            # Quit immediately
            elif (action == 'q'):
                print("Quitting")
                quit()


    elif (action == 'n'):
        print('----------------------------------------')
        print("Networks:")
        core_client = oci.core.VirtualNetworkClient(config)
        list_vcns_response = core_client.list_vcns(compartment_id=compart)
        if DEBUG: print(list_vcns_response.data)
        for i in list_vcns_response.data:
            print("VNC Name=",i.display_name)

    elif (action == 's'):
        print('----------------------------------------')
        print("Block Volumes")
        core_client = oci.core.BlockstorageClient(config)
        list_volumes_response = core_client.list_volumes(compartment_id=compart)
        for i in list_volumes_response.data:
            print("Name=",i.display_name," Size=",i.size_in_gbs," GB")

        print('----------------------------------------')
        print("Boot Volumes")
        core_client = oci.core.BlockstorageClient(config)
        list_boot_volumes_response = core_client.list_boot_volumes(compartment_id=compart)
        for i in list_boot_volumes_response.data:
            print("Name=",i.display_name," Size=",i.size_in_gbs," GB")
        print('----------------------------------------')

        print("Object Storage Buckets")
        object_storage_client = oci.object_storage.ObjectStorageClient(config)
        namespace = object_storage_client.get_namespace().data
        list_buckets_response = object_storage_client.list_buckets(
            namespace_name=namespace,
            compartment_id=compart)
        for i in list_buckets_response.data:
            print("Bucket Name=",i.name)

    elif (action == 'i'):
        print('----------------------------------------')
        print("Container images")
        artifacts_client = oci.artifacts.ArtifactsClient(config)
        list_container_images_response = artifacts_client.list_container_images(
            compartment_id=compart)
        my_container_im = list_container_images_response.data.items
        if DEBUG: print(my_container_im)
        for i in my_container_im:
            print("Name: ", i.display_name)

        print('----------------------------------------')
        print("Container Repos")
        list_container_repositories_response = artifacts_client.list_container_repositories(
            compartment_id=compart)
        if DEBUG: print(list_container_repositories_response.data.items)
        for i in list_container_repositories_response.data.items:
            print("Name: ", i.display_name)

# Rerun script to list instances and follow-up states
    elif (action == 'q'):
        print("Quitting")
        quit()