# Contributing to HomeTax Scraper

Thank you for considering contributing to HomeTax Scraper! 🎉

## 📋 Table of Contents

- [Code of Conduct](#code-of-conduct)
- [How Can I Contribute?](#how-can-i-contribute)
- [Development Setup](#development-setup)
- [Coding Standards](#coding-standards)
- [Testing](#testing)
- [Submitting Changes](#submitting-changes)

## Code of Conduct

This project and everyone participating in it is governed by our Code of Conduct. By participating, you are expected to uphold this code.

## How Can I Contribute?

### 🐛 Reporting Bugs

Before creating bug reports, please check the existing issues as you might find out that you don't need to create one. When you are creating a bug report, please include as many details as possible using our [bug report template](.github/ISSUE_TEMPLATE/bug_report.md).

### 💡 Suggesting Enhancements

Enhancement suggestions are tracked as GitHub issues. When creating an enhancement suggestion, please use our [feature request template](.github/ISSUE_TEMPLATE/feature_request.md).

### 🔧 Pull Requests

1. Fork the repo and create your branch from `main`
2. If you've added code that should be tested, add tests
3. Ensure the test suite passes
4. Make sure your code follows the existing style
5. Write a clear commit message

## Development Setup

### Prerequisites

- **Node.js** 18+ (for CDK)
- **Python** 3.11+ (for Lambda)
- **Docker** (for container builds)
- **AWS CLI** (configured)
- **Git**

### Local Development

1. **Clone the repository**
   ```bash
   git clone https://github.com/danny-zent/hometax-scraper.git
   cd hometax-scraper
   ```

2. **Set up Python environment**
   ```bash
   cd lambda
   python3 -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -r requirements.txt
   playwright install chromium
   ```

3. **Set up CDK environment**
   ```bash
   cd cdk
   npm install
   ```

4. **Set up environment variables**
   ```bash
   export SLACK_WEBHOOK_URL="your-webhook-url-here"
   ```

5. **Run local tests**
   ```bash
   # From project root
   ./test-local.sh
   ```

## Coding Standards

### Python Code (Lambda)

- Follow [PEP 8](https://pep8.org/) style guide
- Use type hints where possible
- Write docstrings for functions and classes
- Maximum line length: 100 characters
- Use meaningful variable names

**Example:**
```python
def scrape_banner_images(self) -> List[Dict[str, Any]]:
    """
    홈택스 메인 페이지에서 배너 이미지와 alt 텍스트를 추출합니다.
    
    Returns:
        List[Dict]: 이미지 정보 리스트
    """
    pass
```

### TypeScript Code (CDK)

- Use TypeScript strict mode
- Follow existing naming conventions
- Use meaningful interface names
- Document complex constructs

**Example:**
```typescript
export class HometaxScraperStack extends cdk.Stack {
  constructor(scope: Construct, id: string, props?: cdk.StackProps) {
    // Implementation
  }
}
```

### Commit Messages

We follow [Conventional Commits](https://www.conventionalcommits.org/) format:

```
<type>[optional scope]: <description>

[optional body]

[optional footer(s)]
```

**Types:**
- `feat`: A new feature
- `fix`: A bug fix
- `docs`: Documentation changes
- `style`: Code style changes (formatting, etc.)
- `refactor`: Code refactoring
- `test`: Adding or modifying tests
- `chore`: Build process or auxiliary tool changes

**Examples:**
```
feat(lambda): add retry mechanism for failed scraping
fix(cdk): resolve EventBridge permission issue
docs(readme): update installation instructions
```

## Testing

### Running Tests

1. **Python Tests**
   ```bash
   cd lambda
   source venv/bin/activate
   python -m pytest tests/
   ```

2. **CDK Tests**
   ```bash
   cd cdk
   npm test
   ```

3. **Integration Tests**
   ```bash
   ./test-local.sh
   ```

### Writing Tests

- Write unit tests for new functions
- Include integration tests for major features
- Test error handling scenarios
- Use descriptive test names

**Python Test Example:**
```python
def test_slack_notification_format():
    """Test Slack notification message formatting"""
    notifier = SlackNotifier("dummy-url")
    images = [{"src": "test.png", "alt": "test alt"}]
    # Test implementation
```

## Submitting Changes

### Pull Request Process

1. **Create a feature branch**
   ```bash
   git checkout -b feature/your-feature-name
   ```

2. **Make your changes**
   - Write code following our standards
   - Add tests for new functionality
   - Update documentation as needed

3. **Test your changes**
   ```bash
   # Run all tests
   ./test-local.sh
   
   # Check CDK synthesis
   cd cdk && npx cdk synth
   ```

4. **Commit your changes**
   ```bash
   git add .
   git commit -m "feat: add amazing new feature"
   ```

5. **Push to your fork**
   ```bash
   git push origin feature/your-feature-name
   ```

6. **Create Pull Request**
   - Use a clear, descriptive title
   - Fill out the PR template
   - Link any related issues
   - Request review from maintainers

### PR Checklist

- [ ] Code follows the style guidelines
- [ ] Self-review completed
- [ ] Tests pass locally
- [ ] Documentation updated (if needed)
- [ ] No breaking changes (or documented)
- [ ] Linked to relevant issues

## Getting Help

If you need help with development:

1. Check existing [issues](https://github.com/danny-zent/hometax-scraper/issues)
2. Create a new issue with the `question` label
3. Contact the maintainer: [@danny-zent](https://github.com/danny-zent)

## Recognition

Contributors will be recognized in:
- README.md contributors section
- Release notes for significant contributions
- GitHub contributor insights

Thank you for contributing! 🚀
