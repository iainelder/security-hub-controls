# Security Hub Controls Reference

A [JSONL-formatted](https://jsonlines.org/) scrape of the [AWS Security Hub controls reference](https://docs.aws.amazon.com/securityhub/latest/userguide/securityhub-controls-reference.html), along with a Python program to update it.

Version 1 scrapes the table from the main reference page. See `dump-controls` for the implementation. Execute the script to try it.

Version 2 will scrape the controls page for each service to include all the available data. See the `tutorial` folder for an attempt to do this by adapting the [Scrapy tutorial](https://docs.scrapy.org/en/latest/intro/tutorial.html). To try it, run `poetry install`, enter the folder, and run `scrapy crawl quotes`.

Security Hub has a public API called [ListSecurityControlDefinitions](https://docs.aws.amazon.com/securityhub/1.0/APIReference/API_ListSecurityControlDefinitions.html) provides something similar to version 1 of this data. You need to enabled Security Hub in your AWS account before you can call the API. In any case, the documentation is still the most complete source for the data.

I was inspired by fluggo's [AWS service authorization reference](https://github.com/fluggo/aws-service-auth-reference) and z0ph's [Monitor for AWS Managed IAM Policies](https://github.com/zoph-io/MAMIP).

## Data structure

Each line in `security-hub-controls.jsonl` looks like this when pretty-printed:

```json
{
    "Id": "Account.1",
    "Title": "Security contact information should be provided for an AWS account",
    "ApplicableStandards": [
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
| jq -c '.ApplicableStandards[]' \
| jq -sc '
  group_by(.)
  | map({ApplicableStandard: .[0], ControlCount: length})
  | sort_by(.ControlCount)
  | reverse
  | .[]
'
```

```json
{"ApplicableStandard":"NIST SP 800-53 Rev. 5","ControlCount":227}
{"ApplicableStandard":"AWS Foundational Security Best Practices v1.0.0","ControlCount":211}
{"ApplicableStandard":"Service-Managed Standard: AWS Control Tower","ControlCount":172}
...
```

Which controls are linked to standard `Service-Managed Standard: AWS Control Tower`?

```bash
cat controls.jsonl \
| jq -c '
  select(.ApplicableStandards | contains(["Service-Managed Standard: AWS Control Tower"]))
  | {Id, Title}
'
```

```json
{"Id":"Account.1","Title":"Security contact information should be provided for an AWS account"}
{"Id":"ACM.1","Title":"Imported and ACM-issued certificates should be renewed after a specified time period"}
{"Id":"APIGateway.1","Title":"API Gateway REST and WebSocket API execution logging should be enabled"}
...
```
