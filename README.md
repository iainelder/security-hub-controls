# Security Hub Controls Reference

A [JSONL-formatted](https://jsonlines.org/) scrape of the [AWS Security Hub controls reference](https://docs.aws.amazon.com/securityhub/latest/userguide/securityhub-controls-reference.html), along with a Python program to update it.

Version 1 scrapes the table from the main reference page. See `dump-controls` for the implementation. Execute the script to try it.

Version 2 will scrape the controls page for each service to include all the available data. See the `tutorial` folder for an attempt to do this by adapting the [Scrapy tutorial](https://docs.scrapy.org/en/latest/intro/tutorial.html). To try it, run `poetry install`, enter the folder, and run `scrapy crawl quotes`.

I wrote this because there is no public API in the Security Hub service that provides this data. [DescribeStandardsControls](https://docs.aws.amazon.com/securityhub/1.0/APIReference/API_DescribeStandardsControls.html) provides less data than is available in the documentation and requires Security Hub to be enabled in an AWS account before it returns anything.

I was inspired by fluggo's [AWS service authorization reference](https://github.com/fluggo/aws-service-auth-reference) and z0ph's [Monitor for AWS Managed IAM Policies](https://github.com/zoph-io/MAMIP).

## Data structure

Each line in `security-hub-controls.jsonl` looks like this when pretty-printed:

```json
{
    "Id": "Account.1",
    "Title": "Security contact information should be provided for an AWS account",
    "LinkedStandards": [
        "AWS Foundational Security Best Practices v1.0.0",
        "NIST SP 800-53 Rev. 5"
    ],
    "Severity": "MEDIUM",
    "ScheduleType": "Periodic"
}
```

## Use cases

Fetch the dump for querying locally.

```bash
curl \
--url "https://raw.githubusercontent.com/iainelder/security-hub-controls/main/security-hub-controls.jsonl" \
--output controls.jsonl \
--silent \
--show-error
```

Which controls are rated critical by Security Hub?

```bash
cat controls.jsonl \
| jq -c 'select(.Severity == "CRITICAL") | {Id, Title}'
```

```json
{"Id":"CloudFront.1","Title":"CloudFront distributions should have a default root object configured"}
{"Id":"CloudTrail.6","Title":"Ensure the S3 bucket used to store CloudTrail logs is not publicly accessible"}
{"Id":"CodeBuild.1","Title":"CodeBuild GitHub or Bitbucket source repository URLs should use OAuth"}
...
```

How many controls does each linked standard have?

```bash
cat controls.jsonl \
| jq -c '.LinkedStandards[]' \
| jq -sc '
  group_by(.)
  | map({LinkedStandard: .[0], ControlCount: length})
  | sort_by(.ControlCount)
  | reverse
  | .[]
'
```

```json
{"LinkedStandard":"NIST SP 800-53 Rev. 5","ControlCount":226}
{"LinkedStandard":"AWS Foundational Security Best Practices v1.0.0","ControlCount":207}
{"LinkedStandard":"Service-Managed Standard: AWS Control Tower","ControlCount":163}
...
```

Which controls are linked to standard `Service-Managed Standard: AWS Control Tower`?

```bash
cat controls.jsonl \
| jq -c '
  select(.LinkedStandards | contains(["Service-Managed Standard: AWS Control Tower"]))
  | {Id, Title}
'
```

```json
{"Id":"ACM.1","Title":"Imported and ACM-issued certificates should be renewed after a specified time period"}
{"Id":"APIGateway.1","Title":"API Gateway REST and WebSocket API execution logging should be enabled"}
{"Id":"APIGateway.2","Title":"API Gateway REST API stages should be configured to use SSL certificates for backend authentication"}
...
```
