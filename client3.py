import websocket
import threading
import os
import time
import logging

BUFFER_SIZE = 24 * 1024 * 1024  # 24 MB

logging.basicConfig(level=logging.DEBUG)

def on_message(ws, message):
    logging.info(f"Received message: {message}")
    if message == "FILE_TRANSFER_COMPLETE":
        print("File transfer complete.")
    elif message.startswith("file:"):
        _, sender, filename = message.split(":", 2)
        threading.Thread(target=receive_file, args=(ws, filename)).start()
    else:
        print(message)

def on_error(ws, error):
    logging.error(f"An error occurred: {error}")

def on_close(ws, close_status_code, close_msg):
    logging.info("### closed ###")

def on_open(ws):
    def run(*args):
        username = input("Enter your username: ")
        ws.send(username)
        logging.info(f"Sent username: {username}")

        while True:
            print("\nMenu:")
            print("1. Send a Unicast Message")
            print("2. Send a Multicast Message")
            print("3. Send a Broadcast Message")
            print("4. Send a File")
            print("5. Quit")
            
            choice = input("Enter your choice: ")
            
            if choice == "1":
                recipient = input("Enter the username to send a message to: ")
                message = input("Enter your message: ")
                ws.send(f"unicast:{recipient}:{message}")
                logging.info(f"Sent unicast message to {recipient}: {message}")
                
            elif choice == "2":
                recipients = input("Enter the usernames to send a message to (comma-separated): ")
                message = input("Enter your message: ")
                ws.send(f"multicast:{recipients}:{message}")
                logging.info(f"Sent multicast message to {recipients}: {message}")
                
            elif choice == "3":
                message = input("Enter your broadcast message: ")
                ws.send(f"broadcast:{message}")
                logging.info(f"Sent broadcast message: {message}")
                
            elif choice == "4":
                recipient = input("Enter the username to send a file to: ")
                filename = input("Enter the filename: ")

                if os.path.isfile(filename):
                    ws.send(f"file:{recipient}:{filename}")
                    send_file(ws, filename)
                    logging.info(f"Started sending file {filename} to {recipient}")
                else:
                    logging.error(f"File {filename} not found. Please check the file path and try again.")
                
            elif choice == "5":
                ws.close()
                break
            else:
                logging.error("Invalid choice. Please try again.")

    threading.Thread(target=run).start()

def send_file(ws, file_path):
    try:
        with open(file_path, 'rb') as file:
            while True:
                data = file.read(BUFFER_SIZE)
                if not data:
                    break
                ws.send(data, websocket.ABNF.OPCODE_BINARY)
                time.sleep(0.01)  # Introduce a small delay to avoid sending data too quickly
            ws.send("FILE_TRANSFER_COMPLETE")
            logging.info(f"File {file_path} sent successfully.")
    except Exception as e:
        logging.error(f"Error sending file {file_path}: {e}")

def receive_file(ws, filename):
    try:
        with open(f"received_{os.path.basename(filename)}", 'wb') as file:
            while True:
                data = ws.recv()
                if data == "FILE_TRANSFER_COMPLETE":
                    print(f"Received file {os.path.basename(filename)}")
                    break
                file.write(data)
        print(f"File {os.path.basename(filename)} successfully received and saved.")
    except Exception as e:
        logging.error(f"An error occurred while receiving file {filename}: {e}")

if __name__ == "__main__":
    websocket.enableTrace(True)
    ws = websocket.WebSocketApp("ws://localhost:11005",
                                on_open=on_open,
                                on_message=on_message,
                                on_error=on_error,
                                on_close=on_close)
    ws.run_forever()
