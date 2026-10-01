# CloudHelpDesk

Cloud-based IT Helpdesk System built using AWS, Flask, MySQL, and Amazon S3.

## Project Overview

CloudHelpDesk is a cloud-based ticket management system where users can create IT support tickets and attach files.

The application stores ticket data in Amazon RDS MySQL and ticket attachments in Amazon S3.

## Architecture

```text
User Browser
     |
     v
Flask Application
     |
     +------> Amazon RDS MySQL
     |
     +------> Amazon S3
