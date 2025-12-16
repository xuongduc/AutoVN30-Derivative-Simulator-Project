# <font color="red"><center>**AutoVN30-SSI-API**</center></font>
<br></br>


- [**AutoVN30-SSI-API**](#autovn30-ssi-api)
  - [**I. Create a Virtual Environment for the Project**](#i-create-a-virtual-environment-for-the-project)
    - [**Step 1: Create a virtual environment**](#step-1-create-a-virtual-environment)
    - [**Step 2: Activate the virtual environment**](#step-2-activate-the-virtual-environment)
    - [**Step 3: Install libraries from requirements.txt**](#step-3-install-libraries-from-requirementstxt)
    - [**Step 4: Exit the virtual environment**](#step-4-exit-the-virtual-environment)
  - [**II. Order Types in the Market**](#ii-order-types-in-the-market)
    - [**1. Overview**](#1-overview)
    - [**2. Summary Table**](#2-summary-table)
    - [**3. Detailed Description of Each Order Type**](#3-detailed-description-of-each-order-type)
      - [3.1. LO – Limit Order](#31-lo--limit-order)
      - [3.2. ATO – At The Open](#32-ato--at-the-open)
      - [3.3. ATC – At The Close](#33-atc--at-the-close)
      - [3.4. MP Order – Market Price (HOSE)](#34-mp-order--market-price-hose)
      - [3.5. MTL Order – Market To Limit (HNX)](#35-mtl-order--market-to-limit-hnx)
      - [3.6. MOK Order – Market Or Kill (HNX)](#36-mok-order--market-or-kill-hnx)
      - [3.7. MAK Order – Market And Kill (HNX)](#37-mak-order--market-and-kill-hnx)
      - [3.8. PLO – Post Limit Order (HNX – after-hours)](#38-plo--post-limit-order-hnx--after-hours)
      - [3.9. GTD – Good Till Date](#39-gtd--good-till-date)
  - [**III. Placing a Limit Order (LO)**](#iii-placing-a-limit-order-lo)
    - [**1. Create a `config.ini` file and store secret keys**](#1-create-a-configini-file-and-store-secret-keys)
    - [**2. Enter the OTP code from the SSI mobile app into the `OTPCode` variable**](#2-enter-the-otp-code-from-the-ssi-mobile-app-into-the-otpcode-variable)
    - [**3. Run the main program**](#3-run-the-main-program)




## <font color="blue">**I. Create a Virtual Environment for the Project**</font>
### **Step 1: Create a virtual environment**
```bash
    python -m venv venv
```

### **Step 2: Activate the virtual environment**
*Windows (Command Prompt):*  

        venv\Scripts\activate


Windows (PowerShell)

        .\venv\Scripts\Activate.ps1


macOS/Linux

        source venv/bin/activate


### **Step 3: Install libraries from requirements.txt**

        pip install -r requirements.txt


### **Step 4: Exit the virtual environment**

        deactivate

<br></br>



## <font color="blue">**II. Order Types in the Market**</font>

### **1. Overview**

Common order types:

- **LO** – Limit Order
- **ATO** – At The Open
- **ATC** – At The Close
- **MP** – Market Price
- **MTL** – Market To Limit (HNX)
- **MOK** – Market Or Kill (HNX)
- **MAK** – Market And Kill (HNX)
- **PLO** – Post Limit Order
- **GTD** – Good Till Date
---


### **2. Summary Table**

| Order Code | Name              | Price Required | Price Type             | Validity Period             | Matching / Remaining Behavior                        |
|------------|-------------------|----------------|------------------------|-----------------------------|------------------------------------------------------|
| LO         | Limit Order       | **Yes**        | User-defined price     | Day / Until date (GTD)      | Partial fill, remainder stays in order book          |
| ATO        | At The Open       | **No**         | Opening price          | ATO session only            | Unfilled quantity canceled after ATO                 |
| ATC        | At The Close      | **No**         | Closing price          | ATC session only            | Unfilled quantity canceled after ATC                 |
| MP         | Market Price      | **No**         | Market price           | Continuous trading session  | Partial fill, remainder → LO                         |
| MTL        | Market To Limit   | **No**         | Market → Limit         | Continuous trading session  | Partial fill, remainder → LO                         |
| MOK        | Market Or Kill    | **No**         | Market price           | Immediate                   | Must fill 100% or canceled entirely                  |
| MAK        | Market And Kill   | **No**         | Market price           | Immediate                   | Partial fill, remainder canceled                     |
| PLO        | Post Limit Order  | **No**         | Closing price          | After-hours (15:00–15:15)   | Filled at close price or canceled                    |
| GTD        | Good Till Date    | **Yes**        | Limit price            | Until specified date        | Partial fill, remainder stays until expiration       |

---


### **3. Detailed Description of Each Order Type**

#### 3.1. LO – Limit Order

**Meaning:**
A buy/sell order placed at a **specified limit price** set by the investor. It executes only when there are matching counterparties at the requested price.

**Characteristics:**

- **price_required:** `true`
- **price_type:** `LIMIT`
- **time_in_force:**
  - Intraday: `DAY`
  - With GTD: `GTD` + `expire_date`
- **partial_fill:** allowed; any unfilled portion remains on the order book until expiration.
---


#### 3.2. ATO – At The Open

**Meaning:**
An order used in the **opening auction** to determine the opening price. No specific price is provided and ATO orders are given priority over regular limit orders.

**Characteristics:**

- **price_required:** `false`
- **price_type:** `MARKET_OPEN`
- **session_constraint:** allowed only during the ATO window (e.g., 09:00–09:15).
- **partial_fill:** may be partially filled.
- **order_life:** valid only during the ATO session; if unfilled when the session ends → canceled.
---


#### 3.3. ATC – At The Close

**Meaning:**
Similar to ATO but used to match orders at the **closing price** during the ATC session.

**Characteristics:**

- **price_required:** `false`
- **price_type:** `MARKET_CLOSE`
- **session_constraint:** only during the ATC window (e.g., HOSE: 14:30–14:45).
- **order_life:** if unfilled by the end of the ATC session → canceled.
---


#### 3.4. MP Order – Market Price (HOSE)

**Meaning:**
A buy/sell order executed at the **best current market price** on HOSE.

- Buy MP → matches at the **lowest available sell** price.
- Sell MP → matches at the **highest available buy** price.

If not fully executed, the remaining quantity may be converted into a **LO (Limit Order)** according to exchange/broker rules.

**Characteristics:**

- **price_required:** `false`
- **price_type:** `MARKET`
- **partial_fill:** allowed; the remainder may be converted to LO or canceled depending on rules.
- **time_in_force:** typically `IOC` or exchange-specific logic (broker-defined).
---


#### 3.5. MTL Order – Market To Limit (HNX)

**Meaning:**
- Executes immediately at **market price**.
- Any unfilled portion is **converted to a LO (Limit Order)** at the most recently matched price.

**Characteristics:**

- **price_required:** `false`
- **price_type:** `MARKET_TO_LIMIT`
- **partial_fill:** allowed.
- **remainder_behavior:** remainder → LO (limit) and stays on the order book.
---


#### 3.6. MOK Order – Market Or Kill (HNX)

**Meaning:**
A market order that must be **fully filled or fully canceled** (no partial fills allowed).

**Characteristics:**

- **price_required:** `false`
- **price_type:** `MARKET`
- **time_in_force:** equivalent to `FOK` (Fill Or Kill).
- **partial_fill:** NOT allowed; if there is insufficient counterpart volume → cancel the entire order.
---


#### 3.7. MAK Order – Market And Kill (HNX)

**Meaning:**
A market order that **fills as much as possible**, and any remaining quantity is **immediately canceled** (it is not placed on the book).

**Characteristics:**

- **price_required:** `false`
- **price_type:** `MARKET`
- **time_in_force:** equivalent to `IOC` (Immediate Or Cancel).
- **partial_fill:** allowed; the remainder is canceled.
---


#### 3.8. PLO – Post Limit Order (HNX – after-hours)

**Meaning:**
An order submitted **after market close** (PLO session, approx. 15:00–15:15) that is matched at the **closing price** of the main session.

**Characteristics:**

- **price_required:** `false` (price = closing price).
- **price_type:** `LIMIT_CLOSE` or `POST_CLOSE` (depends on the API).
- **session_constraint:** allowed only during the PLO session.
- **order_life:** if not matched by the end of the PLO session → canceled.
---


#### 3.9. GTD – Good Till Date

**Meaning:**
A limit order with a specific expiration date. The order remains on the book from placement until:
- Filled in full, or
- The specified expiry date is reached, or
- Canceled manually by the investor.

**Characteristics:**

- **price_required:** `true`
- **price_type:** `LIMIT`
- **time_in_force:** `GTD`
- **expire_date:** required.
- **partial_fill:** allowed; any remaining quantity stays on the book until expiry.



## <font color="blue">**III. Placing a Limit Order (LO)**</font>
### **1. Create a `config.ini` file and store secret keys**
```ini
[DEFAULT]
DataConsumerID = 
DataConsumerSecret = 
TradingConsumerID = 
TradingConsumerSecret = 
TradingPrivateKey = 
OTPCode = 
```

### **2. Enter the OTP code from the SSI mobile app into the `OTPCode` variable**
```
OTPCode = <Your_OTP_code>
```

### **3. Run the main program**
```terminal
python -m src.api.main
```
```