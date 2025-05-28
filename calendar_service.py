import datetime
from googleapiclient.discovery import build
# Import the authenticator from your gmail_service script
from gmail_service import get_gmail_service

def check_calendar_availability(service, date_to_check):
    """Checks for busy time slots on a given date."""
    try:
        # Build the calendar service object using the existing credentials
        calendar_service = build('calendar', 'v3', credentials=service.credentials)

        # Set the time range for the entire day
        time_min = date_to_check.isoformat() + "T00:00:00Z" # Start of day in UTC
        time_max = date_to_check.isoformat() + "T23:59:59Z" # End of day in UTC

        print(f"Checking for busy slots on {date_to_check.strftime('%Y-%m-%d')}...")

        freebusy_query = {
            "timeMin": time_min,
            "timeMax": time_max,
            "timeZone": "UTC",
            "items": [{"id": "primary"}] # 'primary' refers to your main calendar
        }

        results = calendar_service.freebusy().query(body=freebusy_query).execute()

        # The 'calendars' object contains the busy intervals
        busy_slots = results['calendars']['primary']['busy']

        if not busy_slots:
            print("-> Calendar is completely free.")
        else:
            print("-> Found busy slots:")
            for slot in busy_slots:
                start = datetime.datetime.fromisoformat(slot['start']).strftime('%I:%M %p')
                end = datetime.datetime.fromisoformat(slot['end']).strftime('%I:%M %p')
                print(f"  - Busy from {start} to {end}")

        return busy_slots

    except Exception as e:
        print(f"An error occurred with the Calendar API: {e}")
        return None


if __name__ == "__main__":
    # 1. Get the authenticated service object (will trigger browser auth if token.json is gone)
    google_service_creds = get_gmail_service()

    if google_service_creds:
        # 2. Check availability for tomorrow
        tomorrow = datetime.date.today() + datetime.timedelta(days=1)
        check_calendar_availability(google_service_creds, tomorrow)