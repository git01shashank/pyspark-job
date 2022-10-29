# Create an Amazon EKS cluster control plane and an EKS nodegroup compute platform in one step.

from __future__ import annotations
from datetime import timedelta
from textwrap import dedent
import os
import sys
sys.path.insert(0,os.path.abspath(os.path.dirname(__file__)))

# The DAG object; we'll need this to instantiate a DAG

from airflow import DAG

# Operators; we need this to operate!
from airflow.operators.bash import BashOperator
#from airflow.providers.cncf.kubernetes.backcompat.volume_mount import VolumeMount
#from airflow.providers.cncf.kubernetes.backcompat.volume import Volume
from airflow.utils.dates import days_ago

#from airflow.providers.cncf.kubernetes.operators.kubernetes_pod import KubernetesPodOperator
from airflow.contrib.operators.kubernetes_pod_operator import KubernetesPodOperator
import os
# These args will get passed on to each operator
# You can override them on a per-task basis during operator initialization


from datetime import datetime

from airflow.models.baseoperator import chain
from airflow.models.dag import DAG
from airflow.providers.amazon.aws.hooks.eks import ClusterStates, NodegroupStates
# from airflow.providers.amazon.aws.operators.eks import (
#     EksCreateClusterOperator,
#     EksDeleteClusterOperator,
#     EksPodOperator,
# )
from os import environ
os.environ['AWS_DEFAULT_REGION'] = 'ap-south-1'

from airflow.providers.amazon.aws.operators.eks import (
    EksCreateClusterOperator,
    EksCreateNodegroupOperator,
    EksDeleteClusterOperator,
    EksDeleteNodegroupOperator,
    EksPodOperator,
)

from airflow.providers.amazon.aws.sensors.eks import EksClusterStateSensor, EksNodegroupStateSensor
from airflow.utils.trigger_rule import TriggerRule
#from tests.system.providers.amazon.aws.utils import ENV_ID_KEY, SystemTestContextBuilder
default_args = {
    'owner': 'yugen',
    'depends_on_past': False,
    'email': ['shashank.mishra@yugen.ai'],
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
    # 'queue': 'bash_queue',
    # 'pool': 'backfill',
    # 'priority_weight': 10,
    # 'end_date': datetime(2016, 1, 1),
    # 'wait_for_downstream': False,
    # 'dag': dag,
    # 'sla': timedelta(hours=2),
    # 'execution_timeout': timedelta(seconds=300),
    # 'on_failure_callback': some_function,
    # 'on_success_callback': some_other_function,
    # 'on_retry_callback': another_function,
    # 'sla_miss_callback': yet_another_function,
    # 'trigger_rule': 'all_success'
}

# sys_test_context_task = (
#     SystemTestContextBuilder().add_variable(ROLE_ARN_KEY).add_variable(SUBNETS_KEY, split_string=True).build()

# )

with DAG(
    'example_eks_with_nodegroup',
    default_args=default_args,
    description='eks_with_single_node',
    schedule_interval=timedelta(days=1),
    start_date=days_ago(1),
    #tags=['python_kubernetes_workflow'],
) as dag:
       # Create an Amazon EKS Cluster control plane without attaching a compute service.

    #test_context = sys_test_context_task()   
    cluster_name='test_cluster_for_nodegroup'
    nodegroup_name='test_nodegroup_name'
    ROLE_ARN_KEY='arn:aws:iam::832344679060:role/AmazonEKSConnectorAgentRole'
    #ROLE_ARN='arn:aws:iam::aws:policy/aws-service-role/AWSServiceRoleForAmazonEKSNodegroup'
    #pkms = boto3.client('kms', region_name='ap-south-1'
    SUBNETS_KEY='subnet-4b250507'
    ROLE_ARN = environ.get('EKS_DEMO_ROLE_ARN', ROLE_ARN_KEY)
    SUBNETS = environ.get('EKS_DEMO_SUBNETS', 'subnet-4b250507 subnet-86cea5fd').split(' ')
    VPC_CONFIG = {
    'subnetIds': SUBNETS,
    'endpointPublicAccess': True,
    'endpointPrivateAccess': False,
}
    create_cluster = EksCreateClusterOperator(
        task_id='create_cluster_and_nodegroup',
        nodegroup_name=nodegroup_name,
        cluster_name=cluster_name,
        cluster_role_arn= ROLE_ARN,
        nodegroup_role_arn='arn:aws:iam::aws:policy/aws-service-role/AWSServiceRoleForAmazonEKSNodegroup',
        resources_vpc_config=VPC_CONFIG,
        compute='nodegroup',
)


    delete_cluster = EksDeleteClusterOperator(
    task_id='delete_cluster',
    cluster_name=cluster_name,
)
    start_pod = EksPodOperator(
        task_id='start_pod',
        pod_name='test_pod',
        cluster_name=cluster_name,
        image='amazon/aws-cli:latest',
        cmds=['sh', '-c', 'echo Test Airflow; date'],
        labels={'demo': 'hello_world'},
        get_logs=True,
        # Delete the pod when it reaches its final state, or the execution is interrupted.
        is_delete_operator_pod=False,
)

create_cluster>>delete_cluster



    