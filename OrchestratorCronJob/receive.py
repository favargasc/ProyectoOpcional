from OrchestratorCronJob import OrchestratorCronJob


def main():
    cjb = OrchestratorCronJob()
    cjb.receive_message()


if __name__ == "__main__":
    main()
