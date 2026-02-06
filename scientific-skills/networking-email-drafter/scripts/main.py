#!/usr/bin/env python3
"""
Networking Email Drafter
Draft professional follow-up emails to contacts made at conferences.
"""

import argparse


class NetworkingEmailDrafter:
    """Draft networking follow-up emails."""
    
    def draft_email(self, contact_name, conference, topic, your_name, tone="professional"):
        """Draft a follow-up email."""
        
        if tone == "formal":
            greeting = f"Dear Dr. {contact_name.split()[-1]},"
            closing = "Sincerely,"
        elif tone == "casual":
            greeting = f"Hi {contact_name.split()[0]},"
            closing = "Best,"
        else:
            greeting = f"Dear {contact_name},"
            closing = "Best regards,"
        
        email = f"""
{greeting}

It was a pleasure meeting you at {conference}. I particularly enjoyed our 
conversation about {topic}.

I would welcome the opportunity to stay in touch as we both work in this area.

{closing}
{your_name}
"""
        return email.strip()
    
    def draft_linkedin_connect(self, contact_name, conference, topic):
        """Draft LinkedIn connection message."""
        message = f"""Hi {contact_name.split()[0]}, it was great meeting you at {conference}. 
I'd love to stay connected and continue our discussion about {topic}."""
        return message


def main():
    parser = argparse.ArgumentParser(description="Networking Email Drafter")
    parser.add_argument("--contact", "-c", required=True, help="Contact name")
    parser.add_argument("--conference", "-conf", required=True, help="Conference name")
    parser.add_argument("--topic", "-t", required=True, help="Discussion topic")
    parser.add_argument("--name", "-n", default="[Your Name]", help="Your name")
    parser.add_argument("--tone", choices=["formal", "casual", "professional"],
                       default="professional", help="Email tone")
    parser.add_argument("--linkedin", action="store_true", help="Generate LinkedIn message")
    
    args = parser.parse_args()
    
    drafter = NetworkingEmailDrafter()
    
    if args.linkedin:
        message = drafter.draft_linkedin_connect(args.contact, args.conference, args.topic)
        print("LinkedIn Connection Message:")
        print("-"*60)
        print(message)
    else:
        email = drafter.draft_email(args.contact, args.conference, args.topic, args.name, args.tone)
        print("Follow-up Email:")
        print("-"*60)
        print(email)


if __name__ == "__main__":
    main()
