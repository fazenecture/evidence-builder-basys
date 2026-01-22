from app.worker_app import WorkerApp

def main():
    WorkerApp().consume()

if __name__ == "__main__":
    main()
