#!/bin/bash

scp root@ecmwfindicohex.vs.mythic-beasts.com:postgres-dump/postgresql.* ./
gunzip postgresql.*.gz