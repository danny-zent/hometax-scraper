#!/usr/bin/env node
import * as cdk from 'aws-cdk-lib';
import { HometaxScraperStack } from '../lib/hometax-scraper-stack';

const app = new cdk.App();

new HometaxScraperStack(app, 'HometaxScraperStack', {
  env: {
    account: process.env.CDK_DEFAULT_ACCOUNT,
    region: process.env.CDK_DEFAULT_REGION || 'ap-northeast-2', // Seoul region
  },
  description: 'HomeTax scraper infrastructure with Lambda and EventBridge scheduler'
});

app.synth();
