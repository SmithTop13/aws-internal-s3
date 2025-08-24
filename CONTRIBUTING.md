# Contributing to AWS S3 Internal Browser

Thank you for considering contributing to the AWS S3 Internal Browser! We welcome contributions from the community.

## How to Contribute

### Reporting Bugs

If you find a bug, please create an issue with:
- **Clear description** of the problem
- **Steps to reproduce** the issue
- **Expected vs actual behavior**
- **Environment details** (OS, Python version, AWS region)
- **Error messages** or logs if applicable

### Suggesting Features

For new features, please:
- **Check existing issues** to avoid duplicates
- **Describe the use case** and why it's valuable
- **Provide implementation ideas** if you have them
- **Consider security implications** for S3 access

### Development Setup

1. **Fork the repository**
   ```bash
   git clone https://github.com/yourusername/aws-internal-s3.git
   cd aws-internal-s3
   ```

2. **Set up development environment**
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   ```

3. **Configure for development**
   ```bash
   export S3_BUCKET_NAME=your-test-bucket
   export FLASK_DEBUG=1
   ```

4. **Run in development mode**
   ```bash
   python app.py
   ```

### Code Style

- **Python**: Follow PEP 8 guidelines
- **JavaScript**: Use modern ES6+ features, consistent indentation
- **HTML/CSS**: Clean, semantic markup with consistent styling
- **Comments**: Add comments for complex logic only
- **Security**: Never commit AWS credentials or sensitive data

### Pull Request Process

1. **Create a feature branch**
   ```bash
   git checkout -b feature/your-feature-name
   ```

2. **Make your changes**
   - Keep commits focused and atomic
   - Write clear commit messages
   - Test your changes thoroughly

3. **Update documentation**
   - Update README.md if needed
   - Add comments for complex code
   - Update API documentation if applicable

4. **Test thoroughly**
   - Test with different file types and sizes
   - Test error conditions
   - Verify ACL functionality works correctly
   - Test on different browsers if UI changes

5. **Submit pull request**
   - Provide clear description of changes
   - Reference related issues
   - Include screenshots for UI changes

### Security Guidelines

- **Never commit credentials** or sensitive data
- **Validate all user inputs** properly
- **Use least-privilege principles** for AWS permissions
- **Sanitize file paths** and names
- **Handle errors gracefully** without exposing system details

### Testing

Currently, the project uses manual testing. Future contributors are welcome to:
- Add unit tests for backend functions
- Add integration tests for API endpoints
- Add frontend testing with appropriate frameworks

### Code Review

All contributions will be reviewed for:
- **Functionality**: Does it work as intended?
- **Security**: Are there any security vulnerabilities?
- **Code quality**: Is the code clean and maintainable?
- **Documentation**: Is it properly documented?

## Getting Help

- **Issues**: Use GitHub issues for bug reports and feature requests
- **Discussions**: Use GitHub discussions for questions and ideas
- **Email**: Contact maintainers for security-related issues

## Recognition

Contributors will be recognized in:
- GitHub contributors list
- Release notes for significant contributions
- README acknowledgments for major features

Thank you for helping make this project better!