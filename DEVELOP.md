# Development

Create dev environment

```
# Create conda env
make env
conda activate {{ coockiecutter.project_name }}
make develop
```

## Testing

```
# Check linting and format
make check
make fmt

# Run tests
make test
```
