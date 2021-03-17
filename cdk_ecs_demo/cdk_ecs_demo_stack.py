# For consistency with other languages, `cdk` is the preferred import name for
# the CDK's core module.  The following line also imports it as `core` for use
# with examples from the CDK Developer's Guide, which are in the process of
# being updated to use `cdk`.  You may delete this import if you don't need it.
from aws_cdk import aws_ec2 as ec2
from aws_cdk import aws_ecs as ecs
from aws_cdk import aws_ecs_patterns as ecs_patterns
from aws_cdk import aws_iam as iam
from aws_cdk import aws_rds as rds
from aws_cdk import core
from aws_cdk import core as cdk


class CdkEcsDemoStack(cdk.Stack):
    def __init__(self, scope: cdk.Construct, construct_id: str, **kwargs) -> None:

        super().__init__(scope, construct_id, **kwargs)
        vpc = ec2.Vpc(self, "MyVPC")
        rds_cluster = rds.ServerlessCluster(
            self,
            "AnotherCluster",
            engine=rds.DatabaseClusterEngine.aurora_postgres(
                version=rds.AuroraPostgresEngineVersion.VER_10_14
            ),
            vpc=vpc,
        )

        cluster = ecs.Cluster(self, "MyCluster", vpc=vpc)

        role = iam.Role(
            self, "MyRole", assumed_by=iam.ServicePrincipal("ecs-tasks.amazonaws.com")
        )
        role.add_to_policy(
            iam.PolicyStatement(resources=["*"], actions=["rds:DescribeDBClusters"])
        )
        fargate_service = ecs_patterns.NetworkLoadBalancedFargateService(
            self,
            "MyFargateService",
            cluster=cluster,
            task_image_options={
                "image": ecs.ContainerImage.from_asset("./fastapi_app"),
                "environment": {
                    "DB_CLUSTER_IDENTIFIER": rds_cluster.cluster_identifier
                },
                "task_role": role,
            },
        )
        fargate_service.service.connections.security_groups[0].add_ingress_rule(
            peer=ec2.Peer.ipv4(vpc.vpc_cidr_block),
            connection=ec2.Port.tcp(80)        
        )
