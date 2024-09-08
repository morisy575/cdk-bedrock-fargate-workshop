from aws_cdk import (
    Fn,
    Stack,
    aws_ec2 as ec2,
    aws_ecs as ecs,
    aws_iam as iam,
    aws_ecs_patterns as ecs_patterns
)
from constructs import Construct


class EcsStack(Stack):

    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)
        
        # The code that defines your stack goes here
        
        vpc = ec2.Vpc(self, "VPC",
            nat_gateways=1,
            ip_addresses=ec2.IpAddresses.cidr("10.0.0.0/16"),
            max_azs=2,
            subnet_configuration=[
                ec2.SubnetConfiguration(name="public",subnet_type=ec2.SubnetType.PUBLIC,cidr_mask=24),
                ec2.SubnetConfiguration(name="private",subnet_type=ec2.SubnetType.PRIVATE_WITH_EGRESS,cidr_mask=24)
            ],
            vpc_name="CdkBedrockVPC"
        )
        
        
        image = ecs.ContainerImage.from_asset("./web_app")
        
        cluster = ecs.Cluster(self, "CdkWSCluster", 
            vpc=vpc
        )
        
        fargate_service = ecs_patterns.ApplicationLoadBalancedFargateService(self, "CdkWSFargateService",
            cluster=cluster,
            cpu=512,
            memory_limit_mib=1024,
            desired_count=1,
            task_image_options=ecs_patterns.ApplicationLoadBalancedTaskImageOptions(
                image=image,
                container_port=8080,
            ),
            public_load_balancer=True
        )
        
        
        fargate_service.task_definition.add_to_task_role_policy(iam.PolicyStatement(
            effect=iam.Effect.ALLOW,
            actions = ["bedrock:*"],
            resources = ["*"],
            )
        ) 
        
        fargate_service.task_definition.add_to_task_role_policy(iam.PolicyStatement(
            effect=iam.Effect.ALLOW,
            actions = ["ssm:GetParameter"],
            resources = ["arn:aws:ssm:*"]
            )
        ) 