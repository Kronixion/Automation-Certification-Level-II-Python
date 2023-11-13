from robocorp.tasks import task
from robocorp import browser

from RPA.Tables import Tables
from RPA.HTTP import HTTP
from RPA.PDF import PDF
from RPA.Archive import Archive
@task
def minimal_task():
    """
    Orders robots from RobotSpareBin Industries Inc.
    Saves the order HTML receipt as a PDF file.
    Saves the screenshot of the ordered robot.
    Embeds the screenshot of the robot to the PDF receipt.
    Creates ZIP archive of the receipts and the images.
    """
    open_robot_order_website()
    close_annoying_modal()
    ordersTable = get_orders()
    for order in ordersTable:
        insert_order_data(order["Head"], order["Body"],order["Legs"],order["Address"])
        receiptFilePath = store_receipt_as_pdf(order["Order number"])
        screenshotFilePath = screenshot_robot(order["Order number"])
        embed_screenshot_to_receipt(screenshotFilePath, receiptFilePath, order["Order number"])
        order_another_robot()
    archive_receipts()


def open_robot_order_website():
    "Navigates to the robot order website."
    browser.goto("https://robotsparebinindustries.com/#/robot-order")

def close_annoying_modal():
    "Closes the pop up which appears on the Order your robot page."
    page = browser.page()
    page.click("#root > div > div.modal > div > div > div > div > div > button.btn.btn-dark")

def order_another_robot():
    "Clicks on order another robot and closes the popup that appears after the page was redirected."
    page = browser.page()
    page.click("#order-another")
    close_annoying_modal()

def get_orders():
    "Download and read the orders file."
    http = HTTP()
    http.download("https://robotsparebinindustries.com/orders.csv",overwrite=True,target_file=".\\output\\")
    library = Tables()
    return library.read_table_from_csv(".\\output\\orders.csv", columns=["Order number","Head","Body","Legs","Address"])
    
def insert_order_data(head, body, legs, shippingAddress):
    "Inserts the order information into the Order your robot! page."
    page = browser.page()
    page.select_option("#head",head)
    page.click("#id-body-"+body)
    page.fill("input[placeholder=\"Enter the part number for the legs\"]",legs)
    page.fill("#address",shippingAddress)
    page.click("#order")
    "The code from below checks if there's an after the robot clicks on the ORDER button."
    errorExists = page.is_visible("#root > div > div.container > div > div.col-sm-7 > div[role=alert]")
    while errorExists:
        page.click("#order")
        errorExists = page.is_visible("#root > div > div.container > div > div.col-sm-7 > div[role=alert]")

def store_receipt_as_pdf(order_number):
    "This stores the receipt information as a PDF."
    page = browser.page()
    receiptLocator = page.locator("#receipt").inner_html()
    pdf = PDF()
    receiptFilePath = ".\\output\\receipts\\"+str(order_number)+".pdf"
    pdf.html_to_pdf(receiptLocator,receiptFilePath)
    return receiptFilePath    

def screenshot_robot(order_number):
    "This function saves a screenshot of the whole page."
    page = browser.page()
    imageLocator = page.locator("#robot-preview-image").inner_html()
    pdf = PDF()
    screenshotFilePath = ".\\output\\screenshots\\"+str(order_number)+".png"
    page.screenshot(path=screenshotFilePath)
    return screenshotFilePath

def embed_screenshot_to_receipt(screenshotFilePath, receiptFilePath, orderNumber):
    "This adds the image as a watermark to the end of the PDF."
    pdf = PDF()
    pdf.add_watermark_image_to_pdf(
        image_path=screenshotFilePath,
        source_path=receiptFilePath, 
        output_path=".\\output\\results\\receipt_"+str(orderNumber)+".pdf"
        )
    
def archive_receipts():
    "The PDFs from the results folder are archived as a ZIP file."
    lib = Archive()
    lib.archive_folder_with_zip(".\\output\\results",".\\output\\receipts.zip",include="*.pdf")