import * as cdk from 'aws-cdk-lib';
import * as lambda from 'aws-cdk-lib/aws-lambda';
import * as events from 'aws-cdk-lib/aws-events';
import * as targets from 'aws-cdk-lib/aws-events-targets';
import * as logs from 'aws-cdk-lib/aws-logs';
import * as iam from 'aws-cdk-lib/aws-iam';
import { Construct } from 'constructs';
import * as path from 'path';

export class HometaxScraperStack extends cdk.Stack {
  constructor(scope: Construct, id: string, props?: cdk.StackProps) {
    super(scope, id, props);

    // Slack Webhook URL을 환경변수에서 가져오기
    const slackWebhookUrl = process.env.SLACK_WEBHOOK_URL;
    if (!slackWebhookUrl) {
      throw new Error('SLACK_WEBHOOK_URL 환경변수가 설정되어 있지 않습니다.');
    }

    // Lambda 함수를 위한 IAM 역할
    const lambdaRole = new iam.Role(this, 'HometaxScraperLambdaRole', {
      assumedBy: new iam.ServicePrincipal('lambda.amazonaws.com'),
      managedPolicies: [
        iam.ManagedPolicy.fromAwsManagedPolicyName('service-role/AWSLambdaBasicExecutionRole'),
      ],
      inlinePolicies: {
        CloudWatchLogsPolicy: new iam.PolicyDocument({
          statements: [
            new iam.PolicyStatement({
              effect: iam.Effect.ALLOW,
              actions: [
                'logs:CreateLogGroup',
                'logs:CreateLogStream',
                'logs:PutLogEvents'
              ],
              resources: ['arn:aws:logs:*:*:*']
            })
          ]
        })
      }
    });

    // CloudWatch 로그 그룹
    const logGroup = new logs.LogGroup(this, 'HometaxScraperLogGroup', {
      logGroupName: '/aws/lambda/hometax-scraper',
      retention: logs.RetentionDays.ONE_WEEK,
      removalPolicy: cdk.RemovalPolicy.DESTROY
    });

    // Lambda 함수 (Container 이미지 기반)
    const scraperFunction = new lambda.DockerImageFunction(this, 'HometaxScraperFunction', {
      functionName: 'hometax-scraper',
      code: lambda.DockerImageCode.fromImageAsset(path.join(__dirname, '../../lambda')),
      timeout: cdk.Duration.minutes(5),
      memorySize: 1024,
      role: lambdaRole,
      logGroup: logGroup,
      environment: {
        SLACK_WEBHOOK_URL: slackWebhookUrl,
        TIMEZONE: 'Asia/Seoul',
        PYTHONUNBUFFERED: '1'
      },
      architecture: lambda.Architecture.X86_64,
      description: 'HomeTax scraper function that extracts banner images and alt texts'
    });

    // EventBridge 스케줄 규칙 - 매일 오전 8시 (KST) = UTC 23:00 (전날)
    const scheduleRule = new events.Rule(this, 'HometaxScraperSchedule', {
      ruleName: 'hometax-scraper-daily-schedule',
      description: 'Trigger HomeTax scraper daily at 8 AM KST',
      schedule: events.Schedule.cron({
        minute: '0',
        hour: '23',  // UTC 23:00 = KST 08:00 (다음날)
        day: '*',
        month: '*',
        year: '*'
      }),
      enabled: true
    });

    // EventBridge 규칙에 Lambda 함수를 타겟으로 추가
    scheduleRule.addTarget(new targets.LambdaFunction(scraperFunction, {
      event: events.RuleTargetInput.fromObject({
        source: 'eventbridge.scheduler',
        timestamp: events.Schedule.rate(cdk.Duration.days(1))
      })
    }));

    // Lambda 함수에 EventBridge로부터 호출될 수 있는 권한 부여
    scraperFunction.addPermission('AllowEventBridge', {
      principal: new iam.ServicePrincipal('events.amazonaws.com'),
      sourceArn: scheduleRule.ruleArn
    });

    // Outputs
    new cdk.CfnOutput(this, 'LambdaFunctionName', {
      value: scraperFunction.functionName,
      description: 'Lambda function name for HomeTax scraper'
    });

    new cdk.CfnOutput(this, 'ScheduleRuleName', {
      value: scheduleRule.ruleName,
      description: 'EventBridge rule name for scheduling'
    });

    new cdk.CfnOutput(this, 'LogGroupName', {
      value: logGroup.logGroupName,
      description: 'CloudWatch log group name'
    });

    // 수동 실행을 위한 테스트 명령어 출력
    new cdk.CfnOutput(this, 'TestCommand', {
      value: `aws lambda invoke --function-name ${scraperFunction.functionName} --payload '{}' response.json`,
      description: 'Command to manually test the Lambda function'
    });
  }
}
