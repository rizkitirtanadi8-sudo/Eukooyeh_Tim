# Contributing to AI E-commerce Product Manager

Thank you for your interest in contributing! 🎉

## 🚀 Getting Started

1. **Fork the repository**
2. **Clone your fork**
   ```bash
   git clone https://github.com/your-username/ai-ecommerce-manager.git
   cd ai-ecommerce-manager
   ```
3. **Create a branch**
   ```bash
   git checkout -b feature/your-feature-name
   ```

## 💻 Development Setup

### Backend
```bash
cd backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
# Edit .env with your credentials
uvicorn app.main:app --reload
```

### Frontend
```bash
cd frontend
npm install
cp .env.example .env.local
# Edit .env.local
npm run dev
```

## 📝 Code Style

### Python (Backend)
- Follow PEP 8
- Use type hints
- Write docstrings for functions
- Keep functions small and focused

Example:
```python
def create_product(product_data: dict) -> Product:
    """
    Create a new product.
    
    Args:
        product_data: Dictionary containing product information
        
    Returns:
        Created product object
    """
    # Implementation
    pass
```

### TypeScript (Frontend)
- Use TypeScript strict mode
- Follow ESLint rules
- Use functional components
- Prefer hooks over class components

Example:
```typescript
interface ProductProps {
  name: string;
  price: number;
}

export function ProductCard({ name, price }: ProductProps) {
  // Implementation
}
```

## 🧪 Testing

### Backend Tests
```bash
cd backend
pytest
```

### Frontend Tests
```bash
cd frontend
npm test
```

## 📦 Commit Guidelines

Use conventional commits:

- `feat:` New feature
- `fix:` Bug fix
- `docs:` Documentation changes
- `style:` Code style changes (formatting)
- `refactor:` Code refactoring
- `test:` Adding tests
- `chore:` Maintenance tasks

Example:
```bash
git commit -m "feat: add Shopify product sync"
git commit -m "fix: resolve dark mode contrast issue"
git commit -m "docs: update API documentation"
```

## 🔄 Pull Request Process

1. **Update documentation** if needed
2. **Add tests** for new features
3. **Ensure all tests pass**
4. **Update README.md** if adding features
5. **Create Pull Request** with clear description

### PR Template
```markdown
## Description
Brief description of changes

## Type of Change
- [ ] Bug fix
- [ ] New feature
- [ ] Breaking change
- [ ] Documentation update

## Testing
- [ ] Tests added
- [ ] All tests passing
- [ ] Manual testing completed

## Screenshots (if applicable)
Add screenshots here
```

## 🐛 Reporting Bugs

Use GitHub Issues with:
- Clear title
- Steps to reproduce
- Expected vs actual behavior
- Screenshots if applicable
- Environment details

## 💡 Feature Requests

We welcome feature requests! Please:
- Check existing issues first
- Provide clear use case
- Explain expected behavior
- Consider implementation complexity

## 📚 Documentation

- Update README.md for user-facing changes
- Add inline comments for complex logic
- Update API documentation
- Include examples

## 🤝 Code Review

All submissions require review. We'll:
- Check code quality
- Verify tests
- Review documentation
- Suggest improvements

## ⚖️ License

By contributing, you agree that your contributions will be licensed under the MIT License.

## 🙏 Thank You!

Every contribution helps make this project better!
