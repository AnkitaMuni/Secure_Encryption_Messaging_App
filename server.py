import tkinter as tk
from tkinter import messagebox, filedialog
import threading
import socket
import emoji
from encryption import encrypt_message, decrypt_message
from config import SERVER_IP, PORT, KEY
from datetime import datetime
import time
import os
from PIL import Image, ImageTk

class ChatServer:
    def __init__(self, root):
        self.root = root
        self.root.title("Server - Secure Chat")
        self.root.geometry("600x700")
        self.clients = []
        self.running = True
        self.dark_mode = True
        self.emoji_list = ["😊", "😂", "❤️", "👍", "😍", "😎", "🙏", "🎉", "🔥", "💯"]

        self.create_widgets()
        self.bind_keys()
        self.toggle_theme()

        self.server_thread = threading.Thread(target=self.start_server, daemon=True)
        self.server_thread.start()

    def create_widgets(self):
        # Chat window
        self.chat_window = tk.Text(self.root, height=25, width=70, wrap=tk.WORD, bd=0, padx=10, pady=10)
        self.chat_window.pack(pady=30)  # Adjusted padding
        self.chat_window.config(state=tk.DISABLED)

        # Emoji frame
        emoji_frame = tk.Frame(self.root)
        emoji_frame.pack(pady=10)

        for i, emoji_char in enumerate(self.emoji_list):
            btn = tk.Button(emoji_frame, text=emoji_char, font=("Arial", 14),
                            command=lambda e=emoji_char: self.insert_emoji(e))
            btn.grid(row=0, column=i, padx=5)

        # Entry box
        self.entry = tk.Entry(self.root, width=50)
        self.entry.pack(pady=10)

        # Button frame
        button_frame = tk.Frame(self.root)
        button_frame.pack()

        self.send_button = tk.Button(button_frame, text="Send", command=self.send_msg)
        self.send_button.grid(row=0, column=0, padx=5)

        self.image_button = tk.Button(button_frame, text="Send Image", command=self.send_image)
        self.image_button.grid(row=0, column=1, padx=5)

        self.theme_button = tk.Button(button_frame, text="Toggle Theme", command=self.toggle_theme)
        self.theme_button.grid(row=0, column=2, padx=5)

        self.exit_button = tk.Button(button_frame, text="Exit", command=self.close_chat)
        self.exit_button.grid(row=0, column=3, padx=5)

    def bind_keys(self):
        self.root.bind('<Return>', lambda event: self.send_msg())

    def insert_emoji(self, emoji_char):
        self.entry.insert(tk.END, emoji_char)

    def toggle_theme(self):
        bg = "#2E2E2E" if self.dark_mode else "#FFFFFF"
        fg = "#FFFFFF" if self.dark_mode else "#000000"
        entry_bg = "#3C3F41" if self.dark_mode else "#FFFFFF"
        self.root.config(bg=bg)
        self.chat_window.config(bg=bg, fg=fg)
        self.entry.config(bg=entry_bg, fg=fg)
        self.dark_mode = not self.dark_mode

    def start_server(self):
        server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_socket.bind((SERVER_IP, PORT))
        server_socket.listen()

        print("[SERVER] Server started...")

        while self.running:
            try:
                conn, addr = server_socket.accept()
                self.clients.append(conn)
                print(f"[SERVER] Connected to {addr}")
                client_thread = threading.Thread(target=self.handle_client, args=(conn,), daemon=True)
                client_thread.start()
            except:
                break

    def handle_client(self, conn):
        try:
            while self.running:
                data = conn.recv(1024*1024)  # Increased buffer size for images
                if not data:
                    break
                    
                # Check if it's an image
                if data.startswith(b'IMAGE:'):
                    # Handle image
                    image_data = data[6:]  # Remove 'IMAGE:' prefix
                    self.display_image("Client", image_data, align="left")
                else:
                    # Handle regular message
                    decrypted_msg = decrypt_message(KEY, data)
                    print(f"[SERVER] Received encrypted message: {data.hex()}")
                    print(f"[SERVER] Decrypted message: {decrypted_msg}")
                    self.display_message("Client", decrypted_msg, bubble_color="green", align="left")
        except Exception as e:
            print(f"[SERVER] Error handling client: {e}")
        finally:
            conn.close()
            self.clients.remove(conn)
            self.display_message("System", "Client disconnected. Closing server in 3 seconds...", "red", align="center")
            self.chat_window.update()
            time.sleep(3)
            self.close_chat()

    def display_message(self, sender, msg, bubble_color="blue", align="right"):
        self.chat_window.config(state=tk.NORMAL)
        timestamp = datetime.now().strftime("%I:%M %p")
        full_msg = f"{sender} ({timestamp}):\n{emoji.emojize(msg)}\n\n"
        self.chat_window.insert(tk.END, full_msg)

        tag = f"tag_{align}_{bubble_color}"
        self.chat_window.tag_add(tag, "end-3l", "end-1l")
        self.chat_window.tag_config(tag, background=bubble_color, foreground="white",
                                    justify=align, font=("Arial", 12), spacing1=5,
                                    lmargin1=20 if align == "left" else 150,
                                    rmargin=20 if align == "right" else 150)
        self.chat_window.config(state=tk.DISABLED)
        self.chat_window.yview(tk.END)
        
    def display_image(self, sender, image_data, align="right"):
        self.chat_window.config(state=tk.NORMAL)
        timestamp = datetime.now().strftime("%I:%M %p")
        
        # Create a temporary image file
        temp_file = "temp_img_server.jpg"
        with open(temp_file, "wb") as f:
            f.write(image_data)
            
        # Display sender info
        self.chat_window.insert(tk.END, f"{sender} ({timestamp}):\n")
        
        try:
            # Display image
            img = Image.open(temp_file)
            img.thumbnail((300, 300))  # Resize to fit in chat
            photo = ImageTk.PhotoImage(img)
            
            self.chat_window.image_create(tk.END, image=photo)
            self.chat_window.image = photo  # Keep reference
            
            self.chat_window.insert(tk.END, "\n\n")
            
            # Configure tag for alignment
            tag = f"img_tag_{align}"
            self.chat_window.tag_add(tag, "end-3l", "end-1l")
            self.chat_window.tag_config(tag, justify=align)
        except Exception as e:
            self.chat_window.insert(tk.END, f"[Image display error: {str(e)}]\n\n")
        
        self.chat_window.config(state=tk.DISABLED)
        self.chat_window.yview(tk.END)
        try:
            os.remove(temp_file)  # Clean up
        except:
            pass

    def send_msg(self):
        msg = self.entry.get().strip()
        if msg:
            encrypted_msg = encrypt_message(KEY, msg)
            print(f"[SERVER] Sending message: {msg}")
            print(f"[SERVER] Encrypted message: {encrypted_msg.hex()}")
            for client in self.clients:
                try:
                    client.send(encrypted_msg)
                except:
                    self.clients.remove(client)
            self.display_message("Server", msg, bubble_color="blue", align="right")
            self.entry.delete(0, tk.END)
            
    def send_image(self):
        file_path = filedialog.askopenfilename(filetypes=[("Image Files", "*.jpg *.jpeg *.png")])
        if file_path:
            try:
                # Create temp file path in the same directory as the original
                temp_file = os.path.join(os.path.dirname(file_path), "temp_compressed_server.jpg")
                
                # Compress image if too large
                img = Image.open(file_path)
                if os.path.getsize(file_path) > 1024*1024:  # 1MB
                    img.save(temp_file, quality=50)
                    with open(temp_file, "rb") as f:
                        image_data = f.read()
                    os.remove(temp_file)  # Remove only if we created it
                else:
                    with open(file_path, "rb") as f:
                        image_data = f.read()
                
                # Prefix with 'IMAGE:' to identify as image data
                image_data = b'IMAGE:' + image_data
                
                for client in self.clients:
                    try:
                        client.send(image_data)
                    except:
                        self.clients.remove(client)
                
                self.display_image("Server", image_data[6:], align="right")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to send image: {str(e)}")

    def close_chat(self):
        self.running = False
        for client in self.clients:
            try:
                client.close()
            except:
                pass
        self.root.quit()

if __name__ == "__main__":
    root = tk.Tk()
    app = ChatServer(root)
    root.mainloop()