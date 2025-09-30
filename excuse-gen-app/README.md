# Excuse Email Draft Tool

A complete web application for generating professional excuse emails using Databricks Model Serving LLM. Built with FastAPI backend and React frontend, designed to work locally and deploy seamlessly to Databricks Apps.

## 🚀 Features

- **AI-Powered Email Generation**: Uses Databricks Model Serving LLM to create contextually appropriate excuse emails
- **Customizable Parameters**: Choose from 6 categories, 3 tones, and 5 seriousness levels
- **Modern UI**: Clean, responsive design with React and Tailwind CSS
- **Real-time Generation**: Instant email generation with loading states and error handling
- **Copy to Clipboard**: One-click copying of generated emails
- **Databricks Apps Ready**: Optimized for deployment to Databricks Apps platform

## 📁 Project Structure

```
excuse-gen-app/
├── app.yaml                    # Databricks Apps configuration
├── requirements.txt            # Python dependencies
├── src/
│   └── app.py                 # FastAPI backend
├── public/
│   └── index.html             # React frontend (single file)
├── env.example                # Environment variables template
├── .gitignore                 # Git ignore rules
└── README.md                  # This file
```

## 🛠️ Technology Stack

### Backend
- **FastAPI**: Modern, fast web framework for building APIs
- **Uvicorn**: ASGI server for serving the application
- **Pydantic**: Data validation using Python type annotations
- **httpx**: Async HTTP client for calling Databricks Model Serving
- **python-dotenv**: Environment variable management

### Frontend
- **React**: JavaScript library for building user interfaces
- **Tailwind CSS**: Utility-first CSS framework for styling
- **CDN-based**: No build process required, works with CDN imports

### Deployment
- **Databricks Apps**: Cloud-native deployment platform
- **Port 8000**: Optimized for Databricks Apps requirements
- **Environment Variables**: Secure configuration management

## 🚀 Quick Start

### Local Development

1. **Clone and Setup**
   ```bash
   git clone <repository-url>
   cd excuse-gen-app
   ```

2. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure Environment**
   ```bash
   cp env.example .env
   # Edit .env with your Databricks credentials
   ```

4. **Run the Application**
   ```bash
   python -m uvicorn src.app:app --host 0.0.0.0 --port 8000 --reload
   ```

5. **Access the App**
   Open your browser and navigate to: `http://localhost:8000`

### Environment Variables

Create a `.env` file with the following variables:

```env
# Databricks Configuration
DATABRICKS_API_TOKEN=your_databricks_personal_access_token
DATABRICKS_ENDPOINT_URL=https://dbc-32cf6ae7-cf82.staging.cloud.databricks.com/serving-endpoints/databricks-gpt-oss-120b/invocations

# Server Configuration
PORT=8000
HOST=0.0.0.0
```

## 🎯 Usage

### Form Parameters

1. **Category**: Choose from 6 predefined categories
   - Running Late
   - Missed Meeting
   - Deadline
   - WFH/OOO
   - Social
   - Travel

2. **Tone**: Select the email tone
   - Sincere: Professional and apologetic
   - Playful: Light and humorous
   - Corporate: Formal business communication

3. **Seriousness Level**: Adjust from 1 (very silly) to 5 (very serious)
   - 1: Very Silly - Humorous and light-hearted
   - 2: Playful - Casual with some humor
   - 3: Balanced - Professional but approachable
   - 4: Serious - Formal and professional
   - 5: Very Serious - Highly formal and apologetic

4. **Required Fields**:
   - Recipient Name: Who will receive the email
   - Sender Name: Your name for the signature

5. **Optional Fields**:
   - ETA/When: Specific timing information

### Generated Output

The tool generates:
- **Subject Line**: Contextually appropriate email subject
- **Email Body**: Complete email with greeting, apology, reason, next steps, and sign-off
- **Copy Functionality**: One-click copying to clipboard

## 🚀 Deployment to Databricks Apps

### Prerequisites

1. **Databricks Workspace**: Access to a Databricks workspace with Apps enabled
2. **Model Serving Endpoint**: Active Databricks Model Serving endpoint
3. **App Secret**: Configured secret with key `databricks_token`

### Deployment Steps

1. **Configure App Secret**
   ```bash
   # In your Databricks workspace, create an app secret
   # Key: databricks_token
   # Value: your_databricks_personal_access_token
   ```

2. **Deploy the Application**
   ```bash
   databricks apps deploy excuse-gen-app --source-code-path /path/to/excuse-gen-app
   ```

3. **Access Your App**
   - Navigate to your Databricks workspace
   - Go to Apps section
   - Launch your deployed application

### Configuration

The `app.yaml` file contains the Databricks Apps configuration:

```yaml
command: [
  "uvicorn",
  "src.app:app",
  "--host", "0.0.0.0",
  "--port", "8000"
]

env:
  - name: 'DATABRICKS_API_TOKEN'
    valueFrom: databricks_token  # References App secret
  - name: 'DATABRICKS_ENDPOINT_URL'
    value: "https://dbc-32cf6ae7-cf82.staging.cloud.databricks.com/serving-endpoints/databricks-gpt-oss-120b/invocations"
  - name: 'PORT'
    value: "8000"
  - name: 'HOST'
    value: "0.0.0.0"
```

## 🔧 API Endpoints

### Main Endpoints

- `POST /api/generate-excuse` - Generate excuse email
- `GET /` - Serve React application

### Health Check Endpoints

- `GET /health` - Health check
- `GET /healthz` - Alternative health check
- `GET /ready` - Readiness check
- `GET /ping` - Ping endpoint
- `GET /metrics` - Prometheus metrics
- `GET /debug` - Environment debugging

### Request Format

```json
{
  "category": "Running Late",
  "tone": "Playful",
  "seriousness": 3,
  "recipient_name": "Alex",
  "sender_name": "Mona",
  "eta_when": "15 minutes"
}
```

### Response Format

```json
{
  "subject": "Running Late - ETA 15 minutes",
  "body": "Dear Alex,\n\nI wanted to let you know...\n\nBest regards,\nMona",
  "success": true,
  "error": null
}
```

## 🎨 UI/UX Features

### Design Principles
- **Modern**: Clean, minimal interface using Tailwind CSS
- **Responsive**: Mobile-first design that works on all devices
- **Accessible**: Proper labels, keyboard navigation, focus indicators
- **Interactive**: Hover states, loading animations, success feedback

### Layout
- **Two-Column Design**: Form on left, output on right
- **Equal Height Panels**: Consistent visual balance
- **Professional Styling**: Bordered cards with shadows and rounded corners
- **Color Scheme**: Primary blue (#3b82f6) with gray accents

### User Experience
- **Form Validation**: Required field validation with clear error messages
- **Loading States**: Visual feedback during API calls
- **Error Handling**: User-friendly error messages
- **Success Feedback**: Copy confirmation and success states
- **Clear Functionality**: Reset all fields with one click

## 🔍 Technical Specifications

### FastAPI Backend
- **CORS Middleware**: Allows React frontend to make API calls
- **Request Logging**: Comprehensive logging for debugging
- **Error Handling**: Graceful error handling with meaningful messages
- **Static File Serving**: Serves React app with multiple path resolution
- **Async Operations**: Non-blocking HTTP calls to Databricks

### React Frontend
- **Single File**: No build process required, CDN-based
- **State Management**: React hooks for form and output state
- **Form Handling**: Controlled components with validation
- **API Integration**: Fetch API for backend communication
- **Clipboard API**: Native browser clipboard functionality

### Databricks Integration
- **Model Serving**: Direct integration with Databricks Model Serving
- **Authentication**: Bearer token authentication
- **Response Parsing**: Handles multiple LLM response formats
- **Error Recovery**: Fallback strategies for parsing failures

## 🐛 Troubleshooting

### Common Issues

1. **Port 8000 Required**: Databricks Apps requires port 8000
2. **Environment Variables**: Ensure all required env vars are set
3. **CORS Issues**: Backend includes CORS middleware for React
4. **Static Files**: Multiple path resolution for different environments
5. **LLM Responses**: Robust parsing handles various response formats

### Debug Endpoints

- `GET /debug` - Check environment configuration
- `GET /health` - Verify application health
- Check logs for detailed error information

### Local Development Issues

1. **Missing Dependencies**: Run `pip install -r requirements.txt`
2. **Environment Variables**: Copy `env.example` to `.env` and configure
3. **Port Conflicts**: Ensure port 8000 is available
4. **Databricks Access**: Verify API token and endpoint URL

## 📝 License

This project is open source and available under the [MIT License](LICENSE).

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test locally and on Databricks Apps
5. Submit a pull request

## 📞 Support

For issues and questions:
1. Check the troubleshooting section
2. Review the debug endpoint output
3. Check Databricks Apps logs
4. Create an issue in the repository

---

**Happy Excuse Generating! 🎉**
