-- 1. Top 10 Customer IDs & Account Number who made highest total purchases
select
    soh.CustomerID as customer_id,
    soh.AccountNumber as account_number,
    sum(sod.LineTotal) as total_purchase
from sales_order_header soh
join sales_order_details sod
    on soh.SalesOrderID = sod.SalesOrderID
group by soh.CustomerID, soh.AccountNumber
order by total_purchase desc
limit 10;

-- 2. Monthly Sales Trend
select
    YEAR(OrderDate) as year,
    MONTH(OrderDate) as month,
    sum(SubTotal) as monthly_sale
from sales_order_header
group by YEAR(OrderDate), MONTH(OrderDate)
order by year, month;

-- 3. List products and counts where discount perct is 0.02
select
    ProductID,
    count(ProductID) as product_count,
    DiscountPct
from sales_order_details 
where DiscountPct = 0.02
group by ProductID, DiscountPct;

-- 4. find the territory wise sales and adherence to their defined sales quota.
select 
    s.TerritoryID,
    s.SalesTotal,
    q.SalesQuota,
    ROUND((s.SalesTotal / q.SalesQuota) * 100, 2) as AdherencePercentage
from (
    select
        TerritoryID,
        sum(SubTotal) as SalesTotal
    from sales_order_header
    group by TerritoryID)  s
join 
    (select
        TerritoryID,
        sum(SalesQuota) as SalesQuota
    from store_details
    group by TerritoryID)  q
on s.TerritoryID = q.TerritoryID
order by AdherencePercentage;