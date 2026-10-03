# AWS official skills (selected core-skills)

Imported 2026-10-03 from https://github.com/aws/agent-toolkit-for-aws
(verified real: official `aws` GitHub org, "AWS-supported," 2790 stars).
Relevant to the active "Fly.io to AWS Migration Plan" (9 Fly.io apps,
status: active, cost-optimization goal $100+/mo -> $15-35/mo).

The full repo is enterprise-scale (160+ skills spanning quantum computing,
MWAA, Redshift, etc.) -- only pulled the 7 core-skills directly relevant to
a Docker-based container migration:

- `aws-containers` — ECS/Fargate/EKS/ECR, the actual migration target
- `aws-compute` — EC2 if containers aren't the final answer for some app
- `aws-billing-and-cost-management` — the whole point of the migration
- `aws-deployment` — CI/CD pipeline setup
- `aws-networking` — Route 53, CloudFront, etc.
- `signing-in-to-aws` — credential/auth setup
- `aws-database` — RDS/Aurora decision routing (several Fly apps have Postgres)
