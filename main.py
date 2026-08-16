import purchase_order_schedule
import purchase_order_confirmation
import inbound_delivery
import invoice

def main():
    purchase_order_schedule.run()
    purchase_order_confirmation.run()
    inbound_delivery.run()
    invoice.run()

if __name__ == "__main__":
    main()