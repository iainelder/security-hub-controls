# Security Hub Controls Reference

A JSON-formatted scrape of the [AWS Security Hub controls reference](https://docs.aws.amazon.com/securityhub/latest/userguide/securityhub-controls-reference.html), along with a Python program to update it.

Version 1 scrapes the table from the main reference page.

Version 2 will scrape the controls page for each service to include all the available data.

I wrote this because there is no public API in the Security Hub service that provides this data. [DescribeStandardsControls](https://docs.aws.amazon.com/securityhub/1.0/APIReference/API_DescribeStandardsControls.html) provides less data than is available in the documentation and requires Security Hub to be enabled in an AWS account before it returns anything.

Inspired by fluggo's [AWS service authorization reference](https://github.com/fluggo/aws-service-auth-reference) and z0ph's [Monitor for AWS Managed IAM Policies](https://github.com/zoph-io/MAMIP).
