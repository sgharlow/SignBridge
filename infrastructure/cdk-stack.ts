import * as cdk from 'aws-cdk-lib';
import * as lambda from 'aws-cdk-lib/aws-lambda';
import * as apigateway from 'aws-cdk-lib/aws-apigateway';
import * as iot from 'aws-cdk-lib/aws-iot';
import * as s3 from 'aws-cdk-lib/aws-s3';
import * as iam from 'aws-cdk-lib/aws-iam';
import { Construct } from 'constructs';

export class SignToMeStack extends cdk.Stack {
  constructor(scope: Construct, id: string, props?: cdk.StackProps) {
    super(scope, id, props);

    // S3 Bucket for storing processed data and model artifacts
    const dataBucket = new s3.Bucket(this, 'SignToMeDataBucket', {
      bucketName: `signtome-data-${this.account}`,
      removalPolicy: cdk.RemovalPolicy.DESTROY,
      cors: [{
        allowedHeaders: ['*'],
        allowedMethods: [s3.HttpMethods.GET, s3.HttpMethods.POST],
        allowedOrigins: ['*'],
      }]
    });

    // IAM Role for Lambda functions
    const lambdaRole = new iam.Role(this, 'SignToMeLambdaRole', {
      assumedBy: new iam.ServicePrincipal('lambda.amazonaws.com'),
      managedPolicies: [
        iam.ManagedPolicy.fromAwsManagedPolicyName('service-role/AWSLambdaBasicExecutionRole')
      ],
      inlinePolicies: {
        BedrockAccess: new iam.PolicyDocument({
          statements: [
            new iam.PolicyStatement({
              effect: iam.Effect.ALLOW,
              actions: [
                'bedrock:InvokeModel',
                'bedrock:InvokeModelWithResponseStream'
              ],
              resources: ['*']
            })
          ]
        }),
        S3Access: new iam.PolicyDocument({
          statements: [
            new iam.PolicyStatement({
              effect: iam.Effect.ALLOW,
              actions: ['s3:GetObject', 's3:PutObject'],
              resources: [dataBucket.bucketArn + '/*']
            })
          ]
        })
      }
    });

    // Lambda function for sign language processing
    const signProcessorFunction = new lambda.Function(this, 'SignProcessorFunction', {
      runtime: lambda.Runtime.PYTHON_3_9,
      handler: 'handler.process_sign',
      code: lambda.Code.fromAsset('./backend/lambda'),
      role: lambdaRole,
      timeout: cdk.Duration.seconds(30),
      environment: {
        BEDROCK_REGION: this.region,
        DATA_BUCKET: dataBucket.bucketName
      }
    });

    // API Gateway for REST endpoints
    const api = new apigateway.RestApi(this, 'SignToMeApi', {
      restApiName: 'SignToMe API',
      description: 'API for SignToMe sign language interpreter',
      defaultCorsPreflightOptions: {
        allowOrigins: apigateway.Cors.ALL_ORIGINS,
        allowMethods: apigateway.Cors.ALL_METHODS,
        allowHeaders: ['Content-Type', 'Authorization']
      }
    });

    // API Gateway integration
    const signProcessorIntegration = new apigateway.LambdaIntegration(signProcessorFunction);
    
    const processResource = api.root.addResource('process');
    processResource.addMethod('POST', signProcessorIntegration);

    // Note: WebSocket API will be added in Phase 5 for real-time communication

    // IoT Core setup
    const iotRule = new iot.CfnTopicRule(this, 'SignToMeIoTRule', {
      ruleName: 'SignToMeProcessingRule',
      topicRulePayload: {
        sql: "SELECT * FROM 'signtome/frames'",
        actions: [{
          lambda: {
            functionArn: signProcessorFunction.functionArn
          }
        }]
      }
    });

    // Grant IoT permission to invoke Lambda
    signProcessorFunction.addPermission('IoTInvokePermission', {
      principal: new iam.ServicePrincipal('iot.amazonaws.com'),
      sourceArn: iotRule.attrArn
    });

    // Outputs
    new cdk.CfnOutput(this, 'ApiEndpoint', {
      value: api.url,
      description: 'API Gateway endpoint URL'
    });

    new cdk.CfnOutput(this, 'LambdaFunction', {
      value: signProcessorFunction.functionName,
      description: 'Sign processor Lambda function name'
    });

    new cdk.CfnOutput(this, 'DataBucket', {
      value: dataBucket.bucketName,
      description: 'S3 bucket for data storage'
    });
  }
}