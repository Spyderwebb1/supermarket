from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.shortcuts import render
from .models import Item, Category, OrderItem, Order
from django.urls import reverse
from django.http import Http404
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
import stripe
from decimal import Decimal
from .forms import PickUpForm
from django.views.decorators.csrf import csrf_exempt
import datetime

### SET THESE KEYS AS ENVIRONMENT VARIABLES, THEN REFERNECE THE ENVIRONMENT VARIABLE IN CODE!!!!###
# Set your secret key. Remember to switch to your live secret key in production!
# See your keys here: https://dashboard.stripe.com/account/apikeys
stripe.api_key = ''

# If you are testing your webhook locally with the Stripe CLI you
# can find the endpoint's secret by running `stripe listen`
# Otherwise, find your endpoint's secret in your webhook settings in the Developer Dashboard
endpoint_secret = ''

# Create your views here.
def home(request):
    item_count = Item.objects.count()
    category_list = Category.objects.all()
    return render(request, 'catalog/home.html', {
        'item_count': item_count,
        'categories': category_list,
    })



def category_detail(request, pk):
    category = Category.objects.get(pk=pk)
    category_items = Item.objects.filter(category=category).order_by('name')

    category_list = Category.objects.all()
    return render(request, 'catalog/category.html', {
        'items': category_items,
        'category': category,
        'categories': category_list
    })

def items(request):
    items = Item.objects.all().order_by('name')
    category_list = Category.objects.all()
    return render(request, 'catalog/items.html', {
        'items': items,
        'categories': category_list,
        'all_items': True
    })

def item_detail(request, pk):
    try:
        item = Item.objects.get(pk=pk)
    except Item.DoesNotExist:
        raise Http404("Item does not exist")

    category_list = Category.objects.all()
    return render(request, 'catalog/item_detail.html', {
        'item': item,
        'categories': category_list
        })

@login_required
def add_to_cart(request, pk):
    if request.method == 'POST':
        try:
            item = Item.objects.get(pk=pk)
        except Item.DoesNotExist:
            raise Http404("Item does not exist")

        # Get or create user order object
        order, created = Order.objects.get_or_create(
            user = request.user,
            ordered = False,
        )  
        # If open order exists, check if order_item already in order
        if not created:
            order_item = order.orderitems.filter(item=item)
            print(order_item)
            if order_item:
                order_item.quantity += 1
                order_item.save()
            
                return HttpResponseRedirect(reverse('catalog:order-summary'))
        
        order_item = OrderItem.objects.create(
                item=item,
                user=request.user,
                order=order,
            )
        
        #remember to redirect after post request (redirect to order summary page)
        return HttpResponseRedirect(reverse('catalog:order-summary'))

    else:
        return HttpResponseRedirect(reverse('catalog:home'))

@login_required
@require_POST
def update_cart_item(request, pk):
    try:
        order_item = OrderItem.objects.get(pk=pk)
    except OrderItem.DoesNotExist:
        raise Http404("Order item does not exist.")

    quantity = int(request.POST['quantity'])
    
    order_item.quantity = quantity
    order_item.save()
    if order_item.quantity == 0:
        order_item.delete()
    return HttpResponseRedirect(reverse('catalog:order-summary'))

@login_required
def order_summary(request):
    
    try:
        order = Order.objects.get(user=request.user, ordered=False)
        pick_up_form = PickUpForm(instance=order)
            
    except Order.DoesNotExist:
        return render(request, 'catalog/order_summary.html', {
            'error_message': "You do not have any open orders.",
            })
    
    if request.method == 'POST':
        pick_up_form = PickUpForm(request.POST, instance=order)
        pick_up_form.save()
    

    return render(request, 'catalog/order_summary.html', {
        'order': order,
        'pick_up_form': pick_up_form,
        })



@login_required
@require_POST
def checkout(request):
    try:
        order = Order.objects.get(user=request.user, ordered=False)
    except Order.DoesNotExist:
        return render(request, 'catalog/order_summary.html', {
            'categories': category_list,
            'error_message': "You do not have any open orders."
            })
    
    
    successurl = request.build_absolute_uri(reverse('catalog:success'))
    cancelurl = request.build_absolute_uri(reverse('catalog:cancel'))

    total = int(order.get_total() * 100)  # convert to cents, then cast to integer to pass into the API object
    print(f"Total price: {total}")

    session = stripe.checkout.Session.create(
        payment_method_types=['card'],
        line_items=[{
            'price_data': {
                'currency': 'usd',
                'product_data': {
                    'name': 'DW Supermarket Cart',
                },
                'unit_amount': total,
            },
            'quantity': 1,
            }],
        mode='payment',
        client_reference_id=order.id,
        customer_email=request.user.email,
        success_url=successurl,
        cancel_url=cancelurl,
    )
    print(f"Session = {session}")
    return JsonResponse({"id": session.id})

def success(request):
    return render(request, 'catalog/success.html')

def cancel(request):
    return render(request, 'catalog/cancel.html')

@csrf_exempt
@require_POST
def stripe_webhook(request):
    payload = request.body
    sig_header = request.META['HTTP_STRIPE_SIGNATURE']
    event = None
    
    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, endpoint_secret
        )
    except ValueError as e:
        # Invalid payload
        return HttpResponse(status=400)

    except stripe.error.SignatureVerificationError as e:
        # Invalid signature
        return HttpResponse(status=400)

    # Handle the event
    if event.type == 'checkout.session.completed':
        checkout_session = event.data.object # contains a stripe.checkout.session
        fulfill_order(checkout_session)
        print('PaymentIntent was successful!')
    # ... handle other event types
    else:
        print('Unhandled event type {}'.format(event.type))

    return HttpResponse(status=200)

def fulfill_order(checkout_session):
    print("Fulfilling order")
    print(checkout_session)
    order_id = checkout_session.client_reference_id
    order = Order.objects.get(id=order_id)
    order.ordered = True
    
    order.payment_id = checkout_session.payment_intent
    order.ordered_date = datetime.datetime.now()
    order.save()