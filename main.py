import purchase_order_schedule
import purchase_order_confirmation
import inbound_delivery
import invoice
import functions_framework

@functions_framework.http
def main(request):
    purchase_order_schedule.run()
    purchase_order_confirmation.run()
    inbound_delivery.run()
    invoice.run()

if __name__ == "__main__":
    main()