-- Message fact table
-- Contains one row per message with metrics and foreign keys to dimensions

{{ config(materialized='table') }}

with message_facts as (
    select 
        -- Surrogate key
        {{ dbt_utils.generate_surrogate_key(['telegram_message_key']) }} as message_fact_key,
        
        -- Foreign keys
        {{ dbt_utils.generate_surrogate_key(['channel_name']) }} as channel_key,
        {{ dbt_utils.generate_surrogate_key(['message_date']) }} as date_key,
        
        -- Natural keys
        telegram_message_key,
        message_business_key,
        message_id,
        
        -- Dimensions
        channel_name,
        message_date,
        message_timestamp,
        message_hour,
        day_of_week,
        business_date,
        
        -- Message content attributes
        message_text,
        message_length,
        contains_medical_keywords,
        contains_price,
        contains_contact_info,
        
        -- Media attributes
        has_media,
        media_type,
        image_path,
        
        -- Engagement metrics
        coalesce(message_views, 0) as message_views,
        coalesce(message_forwards, 0) as message_forwards,
        
        -- Quality metrics
        data_quality_score,
        is_empty_message,
        is_future_date,
        
        -- Calculated measures
        case when has_media then 1 else 0 end as media_message_count,
        case when contains_medical_keywords then 1 else 0 end as medical_keyword_count,
        case when contains_price then 1 else 0 end as price_mention_count,
        case when contains_contact_info then 1 else 0 end as contact_info_count,
        
        -- Time-based measures
        case when message_hour between 9 and 17 then 1 else 0 end as business_hours_message,
        case when day_of_week in (1,2,3,4,5) then 1 else 0 end as weekday_message,
        
        -- Engagement rate (if views are available)
        case 
            when message_views > 0 then 
                round((message_forwards::numeric / message_views) * 100, 2)
            else 0 
        end as engagement_rate,
        
        -- Metadata
        sender_id,
        scraped_at
        
    from {{ ref('stg_telegram_messages') }}
    where data_quality_score >= 1  -- Include all but completely invalid messages
),

final as (
    select 
        message_fact_key,
        channel_key,
        date_key,
        telegram_message_key,
        message_business_key,
        message_id,
        channel_name,
        message_date,
        message_timestamp,
        message_hour,
        day_of_week,
        business_date,
        message_text,
        message_length,
        contains_medical_keywords,
        contains_price,
        contains_contact_info,
        has_media,
        media_type,
        image_path,
        message_views,
        message_forwards,
        data_quality_score,
        is_empty_message,
        is_future_date,
        media_message_count,
        medical_keyword_count,
        price_mention_count,
        contact_info_count,
        business_hours_message,
        weekday_message,
        engagement_rate,
        sender_id,
        scraped_at,
        
        -- Audit fields
        current_timestamp as created_at,
        current_timestamp as updated_at
        
    from message_facts
)

select * from final
