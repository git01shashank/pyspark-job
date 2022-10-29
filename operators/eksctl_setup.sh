```To install or update eksctl on macOS

The easiest way to get started with Amazon EKS and macOS is by installing eksctl with Homebrew, 
an open-source tool that can be installed using these instructions. The eksctl Homebrew recipe 
installs eksctl and any other dependencies that are required for Amazon EKS, such as kubectl. 
The recipe also installs the aws-iam-authenticator, which is required if you don't have the AWS 
CLI version 1.16.156 or higher installed.```

If you do not already have Homebrew installed on macOS, install it with the following command.

/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/master/install.sh)"

Install the Weaveworks Homebrew tap.

brew tap weaveworks/tap

Install or upgrade eksctl.

Install eksctl with the following command:

brew install weaveworks/tap/eksctl

If eksctl is already installed, run the following command to upgrade:

brew upgrade eksctl && brew link --overwrite eksctl

Test that your installation was successful with the following command.

eksctl version


