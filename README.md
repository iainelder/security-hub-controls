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
    "RelatedRequirements": [
        "NIST.800-53.r5 CM-2",
        "NIST.800-53.r5 CM-2(2)"
    ],
    "Title": "Security contact information should be provided for an AWS account",
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

Which related requirements have the most controls?

```bash
cat controls.jsonl \
| jq -c '.RelatedRequirements[]' \
| jq -sc '
  group_by(.)
  | map({RelatedRequirement: .[0], ControlCount: length})
  | sort_by(.ControlCount)
  | reverse
  | .[]
'
```

```json
{"RelatedRequirement":"NIST.800-53.r5 CA-9(1)","ControlCount":53}
{"RelatedRequirement":"NIST.800-53.r5 SC-7(4)","ControlCount":50}
{"RelatedRequirement":"NIST.800-53.r5 AC-4","ControlCount":49}
...
```

Which controls relate to requirement `NIST.800-53.r5 CA-9(1)`?

```bash
cat controls.jsonl \
| jq -c '
  select(.RelatedRequirements | contains(["NIST.800-53.r5 CA-9(1)"]))
  | {Id, Title}
'
```

```json
{"Id":"Account.2","Title":"AWS accounts should be part of an AWS Organizations organization"}
{"Id":"APIGateway.5","Title":"API Gateway REST API cache data should be encrypted at rest"}
{"Id":"AutoScaling.3","Title":"Auto Scaling group launch configurations should configure EC2 instances to require Instance Metadata Service Version 2 (IMDSv2)"}
...
```
