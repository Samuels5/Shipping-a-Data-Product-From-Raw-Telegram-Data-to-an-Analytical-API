-- Channel dimension table
-- Contains information about each Telegram channel

{{ config(materialized='table') }}

with channel_stats as (
    select 
        channel_name,
        count(*) as total_messages,
        count(case when has_media then 1 end) as total_media_messages,
        round(
            count(case when has_media then 1 end)::numeric / 
            nullif(count(*), 0) * 100, 2
        ) as media_percentage,
        min(message_date) as first_message_date,
        max(message_date) as last_message_date,
        round(avg(message_length), 2) as avg_message_length,
        count(case when contains_medical_keywords then 1 end) as medical_keyword_messages,
        count(case when contains_price then 1 end) as price_mention_messages,
        count(case when contains_contact_info then 1 end) as contact_info_messages
    from {{ ref('stg_telegram_messages') }}
    where data_quality_score >= 2  -- Filter out poor quality messages
    group by channel_name
),

channel_metadata as (
    select 
        channel_name,
        case 
            when channel_name like '%cosmetic%' then 'Cosmetics'
            when channel_name like '%pharma%' then 'Pharmacy'
            when channel_name like '%chemed%' then 'Medical Equipment'
            when channel_name like '%medical%' then 'Medical Supplies'
            else 'General Health'
        end as channel_category,
        
        case 
            when channel_name in ('chemed_et', 'lobelia4cosmetics', 'tikvahpharma') 
            then 'Verified'
            else 'Other'
        end as channel_status,
        
        -- Estimate business type based on content patterns
        case 
            when medical_keyword_messages > total_messages * 0.7 then 'Specialized Medical'
            when price_mention_messages > total_messages * 0.5 then 'Commercial'
            when contact_info_messages > total_messages * 0.3 then 'Service Provider'
            else 'Information/News'
        end as business_type
    from channel_stats
),

final as (
    select 
        -- Surrogate key
        {{ dbt_utils.generate_surrogate_key(['cs.channel_name']) }} as channel_key,
        
        -- Natural key
        cs.channel_name,
        
        -- Metadata
        cm.channel_category,
        cm.channel_status,
        cm.business_type,
        
        -- Statistics
        cs.total_messages,
        cs.total_media_messages,
        cs.media_percentage,
        cs.first_message_date,
        cs.last_message_date,
        cs.avg_message_length,
        cs.medical_keyword_messages,
        cs.price_mention_messages,
        cs.contact_info_messages,
        
        -- Calculated metrics
        case 
            when cs.last_message_date > current_date - interval '7 days' 
            then 'Active'
            when cs.last_message_date > current_date - interval '30 days' 
            then 'Moderate'
            else 'Inactive'
        end as activity_status,
        
        -- Data quality metrics
        round(
            (cs.medical_keyword_messages + cs.price_mention_messages + cs.contact_info_messages)::numeric / 
            nullif(cs.total_messages, 0) * 100, 2
        ) as business_relevance_score,
        
        -- Audit fields
        current_timestamp as created_at,
        current_timestamp as updated_at
        
    from channel_stats cs
    join channel_metadata cm on cs.channel_name = cm.channel_name
)

select * from final
