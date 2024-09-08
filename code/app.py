#!/usr/bin/env python3
import os

import aws_cdk as cdk

from cdk_bedrock_workshop.ecs_stack import EcsStack
from cdk_bedrock_workshop.kb_stack import KbStack


app = cdk.App()
kb_stack = KbStack(app, "KbStack",
    env=cdk.Environment(
        region="us-east-1"
    )
)
ecs_stack = EcsStack(app, "EcsStack")
ecs_stack.add_dependency(kb_stack)

app.synth()
