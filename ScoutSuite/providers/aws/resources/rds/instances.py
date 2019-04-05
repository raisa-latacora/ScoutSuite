from ScoutSuite.providers.aws.resources.regions import Regions
from ScoutSuite.providers.aws.resources.resources import AWSResources


class RDSInstances(AWSResources):
    async def fetch_all(self, **kwargs):
        raw_instances = await self.facade.rds.get_instances(self.scope['region'], self.scope['vpc'])
        for raw_instance in raw_instances:
            name, resource = self._parse_instance(raw_instance)
            self[name] = resource

    def _parse_instance(self, raw_instance):
        instance = {}
        instance['name'] = raw_instance.pop('DBInstanceIdentifier')
        for key in ['InstanceCreateTime', 'Engine', 'DBInstanceStatus', 'AutoMinorVersionUpgrade',
                    'DBInstanceClass', 'MultiAZ', 'Endpoint', 'BackupRetentionPeriod', 'PubliclyAccessible',
                    'StorageEncrypted', 'VpcSecurityGroups', 'DBSecurityGroups', 'DBParameterGroups',
                    'EnhancedMonitoringResourceArn', 'StorageEncrypted']:
            instance[key] = raw_instance[key] if key in raw_instance else None

        instance['is_read_replica'] = self._is_read_replica(raw_instance)
        return instance['name'], instance

    @staticmethod
    def _is_read_replica(instance):
        # The StatusInfos attribute is only defined for read replicas. Ref.: https://bit.ly/2UhKPqP
       return 'ReadReplicaSourceDBInstanceIdentifier' in instance and instance['ReadReplicaSourceDBInstanceIdentifier'] is not None
