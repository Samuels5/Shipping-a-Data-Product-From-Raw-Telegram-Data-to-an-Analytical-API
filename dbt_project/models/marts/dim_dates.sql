-- Date dimension table
-- Contains date attributes for time-based analysis

{{ config(materialized='table') }}

with date_spine as (
    {{ dbt_utils.date_spine(
        datepart="day",
        start_date="cast('2024-01-01' as date)",
        end_date="cast('2026-12-31' as date)"
    ) }}
),

date_attributes as (
    select 
        date_day,
        
        -- Date components
        extract(year from date_day) as year,
        extract(quarter from date_day) as quarter,
        extract(month from date_day) as month,
        extract(week from date_day) as week_of_year,
        extract(day from date_day) as day_of_month,
        extract(dow from date_day) as day_of_week,
        extract(doy from date_day) as day_of_year,
        
        -- Formatted dates
        to_char(date_day, 'YYYY-MM') as year_month,
        to_char(date_day, 'YYYY-Q') as year_quarter,
        to_char(date_day, 'YYYY-"W"WW') as year_week,
        
        -- Day names
        to_char(date_day, 'Day') as day_name,
        to_char(date_day, 'Dy') as day_name_short,
        to_char(date_day, 'Month') as month_name,
        to_char(date_day, 'Mon') as month_name_short,
        
        -- Business attributes
        case 
            when extract(dow from date_day) in (0, 6) then false
            else true
        end as is_weekday,
        
        case 
            when extract(dow from date_day) in (0, 6) then true
            else false
        end as is_weekend,
        
        -- Ethiopian calendar considerations (approximate)
        case 
            when extract(month from date_day) = 9 and extract(day from date_day) = 11 then 'Ethiopian New Year'
            when extract(month from date_day) = 1 and extract(day from date_day) = 19 then 'Timkat'
            when extract(month from date_day) = 5 and extract(day from date_day) = 5 then 'Patriots Day'
            else null
        end as ethiopian_holiday,
        
        -- Relative dates
        case 
            when date_day = current_date then 'Today'
            when date_day = current_date - 1 then 'Yesterday'
            when date_day = current_date + 1 then 'Tomorrow'
            when date_day between current_date - 7 and current_date - 1 then 'Last 7 Days'
            when date_day between current_date - 30 and current_date - 1 then 'Last 30 Days'
            when date_day between current_date + 1 and current_date + 7 then 'Next 7 Days'
            else null
        end as relative_date_label
    from date_spine
),

final as (
    select 
        -- Surrogate key
        {{ dbt_utils.generate_surrogate_key(['date_day']) }} as date_key,
        
        -- Natural key
        date_day,
        
        -- All attributes
        year,
        quarter,
        month,
        week_of_year,
        day_of_month,
        day_of_week,
        day_of_year,
        year_month,
        year_quarter,
        year_week,
        day_name,
        day_name_short,
        month_name,
        month_name_short,
        is_weekday,
        is_weekend,
        ethiopian_holiday,
        relative_date_label,
        
        -- Audit fields
        current_timestamp as created_at
        
    from date_attributes
)

select * from final
