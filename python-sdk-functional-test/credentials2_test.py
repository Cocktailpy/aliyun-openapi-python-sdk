# encoding:utf-8
import json
import os

from alibabacloud.credentials import AccessKeyCredentials, SecurityCredentials
from aliyunsdkcore.auth.credentials import StsTokenCredential, RamRoleArnCredential, EcsRamRoleCredential
from aliyunsdkcore.client import AcsClient
from aliyunsdkros.request.v20150901.DescribeResourceTypesRequest import DescribeResourceTypesRequest
from aliyunsdkecs.request.v20140526.DescribeRegionsRequest import DescribeRegionsRequest
from aliyunsdksts.request.v20150401.AssumeRoleRequest import AssumeRoleRequest

from base import SDKTestBase
from base import disabled

class CredentialsTest(SDKTestBase):

    __name__ = 'CredentialsTest'


    def test_call_request_with_client_config_priority(self):
        request = DescribeRegionsRequest()
        response = self.client._handle_request_in_new_style(request)
        client_credential = id(self.client._credentials_provider.provide())
        config_credential = id(response.http_request.credentials)
        self.assertEqual(client_credential, config_credential)

        response = response.http_response.content
        ret = self.get_dict_response(response)
        self.assertTrue(ret.get("Regions"))
        self.assertTrue(ret.get("RequestId"))

    def test_call_request_with_env_config_priority(self):
        os.environ["ALIBABA_CLOUD_ACCESS_KEY_ID"] = self.access_key_id
        os.environ["ALIBABA_CLOUD_ACCESS_KEY_SECRET"] = self.access_key_secret
        client = AcsClient()
        request = DescribeRegionsRequest()
        response = client._handle_request_in_new_style(request)

        env_credential_id = os.environ.get("ALIBABA_CLOUD_ACCESS_KEY_ID")
        env_credential_secret = os.environ.get("ALIBABA_CLOUD_ACCESS_KEY_SECRET")
        response_key_id = response.http_request.credentials.access_key_id
        response_key_secret = response.http_request.credentials.access_key_secret
        self.assertEqual(env_credential_id, response_key_id)
        self.assertEqual(env_credential_secret, response_key_secret)

        response = response.http_response.content
        ret = self.get_dict_response(response)
        self.assertTrue(ret.get("Regions"))
        self.assertTrue(ret.get("RequestId"))

    def test_call_rpc_request_with_introduction_ak(self):
        request = DescribeRegionsRequest()
        response = self.client._handle_request_in_new_style(request)
        response_credentials = response.http_request.credentials
        self.assertEqual(type(response_credentials), AccessKeyCredentials)

        response = response.http_response.content
        ret = self.get_dict_response(response)
        self.assertTrue(ret.get("Regions"))
        self.assertTrue(ret.get("RequestId"))

    def test_call_roa_request_with_introduction_ak(self):
        request = DescribeResourceTypesRequest()
        response = self.client._handle_request_in_new_style(request)
        response_credentials = response.http_request.credentials
        self.assertEqual(type(response_credentials), AccessKeyCredentials)

        response = response.http_response.content
        ret = self.get_dict_response(response)
        self.assertTrue(ret.get("ResourceTypes"))

    def test_call_rpc_request_with_sts_token(self):
        client = self.init_sub_client()
        self._create_default_ram_role()

        request = AssumeRoleRequest()
        request.set_RoleArn(self.ram_role_arn)
        request.set_RoleSessionName(self.default_role_session_name)
        response = client.do_action_with_exception(request)
        response = self.get_dict_response(response)
        credentials = response.get("Credentials")
        self.assertTrue(credentials["AccessKeyId"].startswith("STS."))

        # Using temporary AK + STS for authentication
        sts_token_credential = StsTokenCredential(
            credentials.get("AccessKeyId"),
            credentials.get("AccessKeySecret"),
            credentials.get("SecurityToken")
        )
        acs_client = AcsClient(
            region_id=self.region_id,
            credential=sts_token_credential)
        request = DescribeRegionsRequest()
        response = acs_client.do_action_with_exception(request)
        ret = self.get_dict_response(response)
        self.assertTrue(ret.get("Regions"))
        self.assertTrue(ret.get("RequestId"))

    def test_call_roa_request_with_sts_token(self):
        client = self.init_sub_client()
        self._create_default_ram_role()
        request = AssumeRoleRequest()
        request.set_RoleArn(self.ram_role_arn)
        request.set_RoleSessionName(self.default_role_session_name)
        response = client.do_action_with_exception(request)
        response = self.get_dict_response(response)
        credentials = response.get("Credentials")
        self.assertTrue(credentials["AccessKeyId"].startswith("STS."))

        # Using temporary AK + STS for authentication
        sts_token_credential = StsTokenCredential(
            credentials.get("AccessKeyId"),
            credentials.get("AccessKeySecret"),
            credentials.get("SecurityToken")
        )
        roa_client = AcsClient(
            region_id=self.region_id,
            credential=sts_token_credential)
        request = DescribeResourceTypesRequest()
        response = roa_client.do_action_with_exception(request)
        ret = self.get_dict_response(response)
        self.assertTrue(ret.get("ResourceTypes"))

    # def test_call_rpc_request_with_ram_role(self):
    #     self._create_default_ram_user()
    #     self._attach_default_policy()
    #     self._create_access_key()
    #     self._create_default_ram_role()
    #
    #     ram_role_arn_credential = RamRoleArnCredential(
    #         self.ram_user_access_key_id,
    #         self.ram_user_access_key_secret,
    #         self.ram_role_arn,
    #         "alice_test")
    #     acs_client = AcsClient(
    #         region_id="cn-hangzhou",
    #         credential=ram_role_arn_credential)
    #     request = DescribeRegionsRequest()
    #     response = acs_client.do_action_with_exception(request)
    #     ret = self.get_dict_response(response)
    #     self.assertTrue(ret.get("Regions"))
    #     self.assertTrue(ret.get("RequestId"))

    # def test_call_roa_request_with_ram_role(self):
    #     self._create_default_ram_user()
    #     self._attach_default_policy()
    #     self._create_access_key()
    #     self._create_default_ram_role()
    #
    #     ram_role_arn_credential = RamRoleArnCredential(
    #         self.ram_user_access_key_id,
    #         self.ram_user_access_key_secret,
    #         self.ram_role_arn,
    #         "alice_test")
    #     roa_client = AcsClient(
    #         region_id="cn-hangzhou",
    #         credential=ram_role_arn_credential)
    #     request = DescribeResourceTypesRequest()
    #     response = roa_client.do_action_with_exception(request)
    #     ret = self.get_dict_response(response)
    #     self.assertTrue(ret.get("ResourceTypes"))

    # def test_call_rpc_request_with_ecs_ram(self):
    #     ecs_ram_role_credential = EcsRamRoleCredential("EcsRamRoleTest")
    #     acs_client = AcsClient(region_id="cn-hangzhou", credential=ecs_ram_role_credential)
    #     request = DescribeRegionsRequest()
    #     response = acs_client.do_action_with_exception(request)

    def test_call_rpc_request_with_env_ak(self):
        os.environ["ALIBABA_CLOUD_ACCESS_KEY_ID"] = self.access_key_id
        os.environ["ALIBABA_CLOUD_ACCESS_KEY_SECRET"] = self.access_key_secret
        client = AcsClient()
        request = DescribeRegionsRequest()
        response = client.do_action_with_exception(request)
        ret = self.get_dict_response(response)
        self.assertTrue(ret.get("Regions"))
        self.assertTrue(ret.get("RequestId"))

    def test_call_roa_request_with_env_ak(self):
        os.environ["ALIBABA_CLOUD_ACCESS_KEY_ID"] = self.access_key_id
        os.environ["ALIBABA_CLOUD_ACCESS_KEY_SECRET"] = self.access_key_secret
        client = AcsClient()
        request = DescribeResourceTypesRequest()
        response = self.client.do_action_with_exception(request)
        ret = self.get_dict_response(response)
        self.assertTrue(ret.get("ResourceTypes"))

    def test_call_rpc_request_with_config_default(self):
        client = AcsClient()
        request = DescribeRegionsRequest()
        response = client.do_action_with_exception(request)
        ret = self.get_dict_response(response)
        self.assertTrue(ret.get("Regions"))
        self.assertTrue(ret.get("RequestId"))

    def test_call_roa_request_with_config_default(self):
        client = AcsClient()
        request = DescribeResourceTypesRequest()
        response = client.do_action_with_exception(request)
        ret = self.get_dict_response(response)
        self.assertTrue(ret.get("ResourceTypes"))

    # def test_call_rpc_request_with_config_ram_role_arn(self):
    #     client = AcsClient()
    #     client._credentials_provider = DefaultChainedCredentialsProvider("ram_role_arn")
    #     request = DescribeRegionsRequest()
    #     response = client.do_action_with_exception(request)
    #     ret = self.get_dict_response(response)
    #     self.assertTrue(ret.get("Regions"))
    #     self.assertTrue(ret.get("RequestId"))
    #
    # def test_call_roa_request_with_config_ram_role_arn(self):
    #     client = AcsClient()
    #     client._credentials_provider = DefaultChainedCredentialsProvider("ram_role_arn")
    #     request = DescribeResourceTypesRequest()
    #     response = client.do_action_with_exception(request)
    #     ret = self.get_dict_response(response)
    #     self.assertTrue(ret.get("ResourceTypes"))



