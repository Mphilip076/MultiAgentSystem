import sys
import os

# Add System/src to path to import the tool
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.join(current_dir, "System", "src"))

def test_email():
    print("--- Starting Email Tool Test ---")
    try:
        from system.crew import send_email_tool
        
        test_message = (
            "Hello!\n\n"
            "This is a standalone test of the Email Sender Tool.\n"
            "If you are reading this, the Gmail API integration is working correctly!\n\n"
            "Best,\n"
            "The System"
        )
        
        print("Attempting to send test email...")
        # The @tool decorator wraps the function, so we use .invoke() to call it
        result = send_email_tool.run("Hello!!!", "Nothing", "Nothing")
        
        print("\nSUCCESS!")
        print(f"Tool Output: {result}")
        
    except ImportError as e:
        print(f"Error: Could not import send_email_tool. Ensure paths are correct. {e}")
    except Exception as e:
        print(f"\nFAILED!")
        print(f"Error: {str(e)}")

if __name__ == "__main__":
    test_email()
