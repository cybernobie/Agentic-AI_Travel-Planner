# 🌍 Agentic AI - Travel Planner

An intelligent travel agent built with **Streamlit**, **LangChain**, and **LangGraph** that creates personalized, complete travel itineraries based on user preferences. The agent utilizes various tools to search for flights, recommend hotels, discover top attractions, fetch weather forecasts, and estimate budgets, providing a comprehensive travel planning experience.

## ✨ Features

- **Personalized Itineraries:** Generates a complete, day-wise travel itinerary based on source, destination, dates, duration, and specific preferences.
- **Flight & Hotel Integration:** Uses tools to search for the best flights and top hotel recommendations based on real-time simulated data, along with a justification for the selections.
- **Places Discovery:** Highlights top attractions and places to visit in your destination city.
- **Weather Forecast:** Integrates with the [Open-Meteo API](https://open-meteo.com/) to provide a 7-day weather forecast, helping you pack and plan appropriately.
- **Budget Estimation:** Automatically estimates the total cost of the trip, breaking down flights, hotels, and daily expenses.
- **Export to PDF:** Allows users to easily download their customized travel summary as a PDF file.
- **Interactive UI:** A beautifully styled, responsive user interface built with Streamlit.

## 🛠️ Technology Stack

- **Frontend:** Streamlit
- **LLM & Agent Framework:** LangChain, LangGraph, Langchain-OpenAI (configured to use Gemini 3 Flash)
- **PDF Generation:** xhtml2pdf, markdown
- **Environment Management:** python-dotenv
- **API Requests:** requests

## 🚀 Getting Started

### Prerequisites

- Python 3.8+
- [Pip](https://pip.pypa.io/en/stable/)

### Installation

1. **Clone the repository:**
   ```bash
   git clone https://github.com/yourusername/agentic-ai-travel-planner.git
   cd agentic-ai-travel-planner
   ```

2. **Create a virtual environment (optional but recommended):**
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # On Windows use: .venv\Scripts\activate
   ```

3. **Install the dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up Environment Variables:**
   Create a `.env` file in the root directory and add your API credentials:
   ```env
   OPENAI_API_KEY=your_api_key_here
   OPENAI_API_BASE=your_api_base_url_here
   ```
   *(Note: The app is currently configured to use `gemini-3-flash` through the OpenAI compatible API.)*

### Running the Application

Start the Streamlit server:
```bash
streamlit run app.py
```
The application will open in your default web browser at `http://localhost:8501`.

## 🧰 Agent Tools (`tools.py`)

The React agent uses the following tools to gather information:
- `flight_search`: Searches for available flights between cities sorted by price.
- `hotel_recommendation`: Provides top hotel recommendations based on the destination city.
- `places_discovery`: Discovers top-rated attractions to visit.
- `weather_lookup`: Fetches the 7-day maximum temperature forecast using geographical coordinates.
- `budget_estimation`: Calculates the overall estimated budget including flights, hotels, and daily allowances.

## 📂 Project Structure

- `app.py`: The main Streamlit application and UI logic, including the LangGraph React agent setup.
- `tools.py`: Contains the definition of all the tools available to the AI agent.
- `requirements.txt`: Python package dependencies.
- `flights.json`, `hotels.json`, `places.json`: Mock data files used by the tools to simulate database/API queries.

## 🤝 Contributing

Contributions, issues, and feature requests are welcome! Feel free to check the [issues page](https://github.com/yourusername/agentic-ai-travel-planner/issues).

## 📝 License

This project is licensed under the MIT License - see the LICENSE file for details.
