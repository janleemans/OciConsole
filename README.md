# coci - interactive Command-Line OCI Console

A Command-line console for interacting with an OCI instance

## Prerequisites

- oci CLI installed (see [OCI CLI Quickstart](https://docs.oracle.com/en-us/iaas/Content/API/SDKDocs/cliinstall.htm#Quickstart)] )
- API key set up on OCI and .oci/config file created
- Tested with Python 3.11.7
- Install python packages `oci` and `readchar`
- Download the coci.py file from this repo

## Objective of this tool

When you are developing on Oracle OCI, you often only need to log in to the Oracle console to spin up or stop your VM's or Databases. With 2-Factor authentication and mandatory long passwords imposed, this is a lot of clicks, keystrokes and waiting for the VM overview page to appear.

Of course there is an OCI Command-line utility you can install on your local machine, but even then you need to actually have a series of OCIDs at the ready to be copied over in order to manage your environments.

This simple Python script will allow you to list and start/stop various OCI components in an easy, interactive way: starting and stopping VM's, DB's, or listing storage or Container resources

## Current capabilities

This is a v1 of the tool, with the core capabilities to quickly start working with OCI resources, or shut them down in the evening when you are done.  More extensive functionality might follow, or feel free to suggest your own improvements trough a pull request.

- Top Menu :
  - g: Go to a different compartment
  - c: Compute instances: list, start or stop
  - n: Networks: list available VCN's
  - s: Storage: list storage buckets and block volumes
  - d: Databases - only autonomous for now: list, start and stop
  - i: CN objects: list containers
  - q: quit

- Sub menus (for now only instances and DB's
  - u: bring an instance UP
  - d: bring an instance DOWN
  - a: print all attributes
  - space: re-list instances
  - -: back to main menu

## Setup

- Download the josi.py file on your machine, for example in the ~/dev folder
- define an alias to have direct access to the command:

```bash
alias joci='python ~/dev/joci.py'
```

## Customizations

You can add an entry called "compartment" in the ~/oci/config file to specify the starting compartment in a tenancy (instead of the default root compartment)

Syntax:

```compartment=ocid1.compartment.oc1..aaaaa...```
