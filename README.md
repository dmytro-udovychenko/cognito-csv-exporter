# 🔐 AWS Cognito User Pool CSV Exporter

[![Python Version](https://img.shields.io/badge/python-3.8%2B-blue.svg)](https://python.org)
[![AWS](https://img.shields.io/badge/AWS-Cognito-orange.svg)](https://aws.amazon.com/cognito/)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![Maintenance](https://img.shields.io/badge/Maintained%3F-yes-green.svg)](https://github.com/dmytro-udovychenko/cognito-csv-exporter/graphs/commit-activity)

> 🚀 **Export Amazon Cognito User Pool users to CSV format with ease!**

A powerful Python script that exports user records from AWS Cognito User Pool to CSV format, perfect for user data migration, backup, or analysis.

## ✨ Features

- 📊 **Bulk Export**: Export all users or specify a maximum number
- 🔄 **Pagination Support**: Handles large user pools automatically
- ⚡ **Fast Processing**: Optimized for performance with configurable limits
- 🛡️ **AWS Profile Support**: Use different AWS profiles for multi-account setups
- 📝 **Customizable Output**: Specify custom file names and paths
- 🔧 **Resume Support**: Continue exports from a specific pagination token
- ✅ **Import Ready**: Generated CSV is optimized for Cognito User Pool imports

## 🛠️ Installation

### Prerequisites

- Python 3.8 or higher
- AWS CLI configured or valid AWS credentials
- Access to AWS Cognito User Pool

### Quick Setup

1. **Clone the repository:**
   ```bash
   git clone https://github.com/dmytro-udovychenko/cognito-csv-exporter.git
   cd cognito-csv-exporter
   ```

2. **Create and activate virtual environment:**
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

## 🚀 Quick Start

### Basic Usage

```bash
# Export all users from a Cognito User Pool
python3 CognitoUserToCSV.py --user-pool-id us-east-1_XXXXXXXXX
```

### With AWS Profile

```bash
# Use specific AWS profile
AWS_PROFILE=myprofile python3 CognitoUserToCSV.py \
  --user-pool-id us-east-1_XXXXXXXXX \
  --profile myprofile
```

### Advanced Usage

```bash
# Export with custom settings
python3 CognitoUserToCSV.py \
  --user-pool-id us-east-1_XXXXXXXXX \
  --region us-west-2 \
  --file-name exported_users.csv \
  --num-records 1000 \
  --profile production
```

## 📋 Command Line Arguments

| Parameter | Required | Description | Default |
|-----------|----------|-------------|---------|
| `--user-pool-id` | ✅ | Cognito User Pool ID | - |
| `--region` | ❌ | AWS region | `us-east-1` |
| `--profile` | ❌ | AWS profile name | Default profile |
| `--file-name` / `-f` | ❌ | Output CSV filename | `CognitoUsers.csv` |
| `--num-records` | ❌ | Maximum records to export | `0` (all) |
| `--starting-token` | ❌ | Resume from pagination token | - |

## 📊 Output Format

The exported CSV includes the following attributes:

| Field | Description |
|-------|-------------|
| `profile` | User profile information |
| `email` | User email address |
| `email_verified` | Email verification status (always `true`) |
| `given_name` | First name |
| `family_name` | Last name |
| `cognito:username` | Cognito username (same as email) |
| `cognito:mfa_enabled` | MFA status |
| _...and more_ | Additional standard Cognito attributes |

### 🔧 Special Features

- **Email Verification**: All exported users have `email_verified` set to `true` for seamless imports
- **Username Mapping**: `cognito:username` is automatically mapped to the user's email
- **MFA Detection**: Automatically detects and exports MFA status

## 💡 Examples

### Export Specific Number of Users

```bash
python3 CognitoUserToCSV.py \
  --user-pool-id us-east-1_XXXXXXXXX \
  --num-records 500 \
  --file-name first_500_users.csv
```

### Resume from Previous Export

```bash
python3 CognitoUserToCSV.py \
  --user-pool-id us-east-1_XXXXXXXXX \
  --starting-token "your-pagination-token" \
  --file-name continued_export.csv
```

### Multi-Region Export

```bash
# Export from different regions
python3 CognitoUserToCSV.py \
  --user-pool-id eu-west-1_YYYYYYYYY \
  --region eu-west-1 \
  --file-name eu_users.csv
```

## 🔍 Troubleshooting

### Common Issues

**Permission Denied:**
```bash
# Ensure your AWS credentials have the required permissions:
# - cognito-idp:ListUsers
# - cognito-idp:DescribeUserPool
```

**Module Not Found:**
```bash
# Make sure you're in the virtual environment
source venv/bin/activate
pip install -r requirements.txt
```

**SSL Certificate Errors:**
```bash
# Update certificates
pip install --upgrade certifi
```

### 📞 Getting Help

If you encounter issues:
1. Check your AWS credentials and permissions
2. Verify the User Pool ID is correct
3. Ensure you have network connectivity to AWS
4. Review the error message for specific details

## 🤝 Contributing

We welcome contributions! Please feel free to submit a Pull Request. For major changes, please open an issue first to discuss what you would like to change.

### Development Setup

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/amazing-feature`
3. Make your changes
4. Test thoroughly
5. Commit: `git commit -m 'Add amazing feature'`
6. Push: `git push origin feature/amazing-feature`
7. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- Original project by [hawkerfun](https://github.com/hawkerfun/cognito-csv-exporter)
- AWS Cognito documentation and community

## 📚 Related Tools

For complete Cognito backup and restore operations, consider:
- [cognito-backup-restore](https://www.npmjs.com/package/cognito-backup-restore) - Full backup solution

---

<div align="center">

**Made with ❤️ for the AWS community**

[Report Bug](https://github.com/dmytro-udovychenko/cognito-csv-exporter/issues) · [Request Feature](https://github.com/dmytro-udovychenko/cognito-csv-exporter/issues) · [Documentation](https://github.com/dmytro-udovychenko/cognito-csv-exporter/wiki)

</div>
