import tkinter as tk
from tkinter import ttk, scrolledtext
import json
import threading
from conexion import conectar_rabbitmq
from productor import publicar_evento_libro


class InterfazLibrosUsados:
    def __init__(self):
        self.ventana = tk.Tk()
        self.configurar_interfaz()

    def configurar_interfaz(self):
        # Configura la interfaz gráfica principal
        self.ventana.title("BookTrade - Plataforma de Libros Usados")
        self.ventana.geometry("700x600")
        self.ventana.configure(bg="#f8f9fa")

        self.crear_seccion_publicacion()
        self.crear_seccion_notificaciones()

    def crear_seccion_publicacion(self):
        # Crea la sección para publicar nuevos libros
        frame_publicar = tk.LabelFrame(
            self.ventana,
            text="Publicar Nuevo Libro",
            bg="#f8f9fa",
            font=("Arial", 12, "bold")
        )
        frame_publicar.pack(pady=15, padx=20, fill="x")

        # Campos del formulario
        tk.Label(frame_publicar, text="Título:", bg="#f8f9fa").grid(row=0, column=0, sticky="w", pady=5)
        self.entry_titulo = tk.Entry(frame_publicar, width=30)
        self.entry_titulo.grid(row=0, column=1, padx=10, pady=5)

        tk.Label(frame_publicar, text="Género:", bg="#f8f9fa").grid(row=1, column=0, sticky="w", pady=5)
        self.combo_genero = ttk.Combobox(
            frame_publicar,
            values=["Ficción", "Ciencia Ficción", "Fantasía", "Romance", "Biografía"],
            state="readonly",
            width=27
        )
        self.combo_genero.grid(row=1, column=1, padx=10, pady=5)
        self.combo_genero.current(0)

        tk.Label(frame_publicar, text="Precio:", bg="#f8f9fa").grid(row=2, column=0, sticky="w", pady=5)
        self.entry_precio = tk.Entry(frame_publicar, width=15)
        self.entry_precio.grid(row=2, column=1, sticky="w", padx=10, pady=5)

        # Botón de publicación
        btn_publicar = tk.Button(
            frame_publicar,
            text="Publicar Libro",
            command=self.publicar_libro,
            bg="#28a745",
            fg="white",
            font=("Arial", 10, "bold")
        )
        btn_publicar.grid(row=3, column=1, pady=15, sticky="e")

    def crear_seccion_notificaciones(self):
        # Crea la sección para mostrar notificaciones
        frame_noti = tk.LabelFrame(
            self.ventana,
            text="Notificaciones en Tiempo Real",
            bg="#f8f9fa",
            font=("Arial", 12, "bold")
        )
        frame_noti.pack(pady=15, padx=20, fill="both", expand=True)

        self.caja_notificaciones = scrolledtext.ScrolledText(
            frame_noti,
            height=20,
            width=80,
            font=("Consolas", 9)
        )
        self.caja_notificaciones.pack(pady=10, padx=10, fill="both", expand=True)

        # Iniciar hilo para escuchar notificaciones
        hilo_consumidor = threading.Thread(
            target=self.escuchar_notificaciones,
            daemon=True
        )
        hilo_consumidor.start()

    def publicar_libro(self):
        """Publica un nuevo libro en el sistema"""
        datos_libro = {
            'titulo': self.entry_titulo.get(),
            'genero': self.combo_genero.get(),
            'precio': self.entry_precio.get(),
            'vendedor': 'usuario_actual'
        }
        try:
            publicar_evento_libro('NUEVO_LIBRO', datos_libro)
            self.mostrar_notificacion("Libro publicado exitosamente")

            # Limpiar campos
            self.entry_titulo.delete(0, tk.END)
            self.entry_precio.delete(0, tk.END)
        except Exception as e:
            self.mostrar_notificacion(f"Error: {str(e)}")

    def escuchar_notificaciones(self):
        """Escucha notificaciones de RabbitMQ"""
        def callback(ch, method, properties, body):
            try:
                notificacion = json.loads(body.decode())
                mensaje = notificacion['mensaje']
                self.ventana.after(0, lambda: self.mostrar_notificacion(mensaje))
            except Exception as e:
                print(f"Error: {e}")

        try:
            canal = conectar_rabbitmq()
            if canal:
                canal.queue_declare(queue='notificaciones')
                canal.basic_consume(
                    queue='notificaciones',
                    on_message_callback=callback,
                    auto_ack=True
                )
                canal.start_consuming()
        except Exception as e:
            print(f"Error en consumidor: {e}")

    def mostrar_notificacion(self, mensaje):
        """Muestra una notificación en la caja de texto"""
        self.caja_notificaciones.insert(tk.END, f"{mensaje}\n")
        self.caja_notificaciones.see(tk.END)

    def ejecutar(self):
        """Ejecuta la aplicación"""
        self.ventana.mainloop()


if __name__ == "__main__":
    app = InterfazLibrosUsados()
    app.ejecutar()