-- Staging model for Telegram messages
-- This model cleans and standardizes the raw telegram message data

{{ config(materialized='view') }}

with source_data as (
    select 
        id,
        message_id,
        channel_name,
        date as message_date,
        text as message_text,
        sender_id,
        has_media,
        media_type,
        image_path,
        scraped_at,
        raw_data
    from {{ source('raw', 'telegram_messages') }}
),

cleaned_data as (
    select 
        id as telegram_message_key,
        message_id,
        
        -- Clean and standardize channel name
        lower(trim(channel_name)) as channel_name,
        
        -- Date fields
        message_date::timestamp as message_timestamp,
        message_date::date as message_date,
        extract(hour from message_date) as message_hour,
        extract(dow from message_date) as day_of_week,
        
        -- Text processing
        coalesce(message_text, '') as message_text,
        length(coalesce(message_text, '')) as message_length,
        
        -- Check for common medical keywords
        case 
            when lower(message_text) like any (array['%pharmacy%', '%medicine%', '%drug%', '%tablet%', '%pill%', '%injection%']) 
            then true 
            else false 
        end as contains_medical_keywords,
        
        -- Extract price information (basic regex for Ethiopian Birr)
        case 
            when message_text ~* '\d+\s*(birr|etb|br)' 
            then true 
            else false 
        end as contains_price,
        
        -- Contact information detection
        case 
            when message_text ~* '(\+251|09\d{8}|call|contact|phone)' 
            then true 
            else false 
        end as contains_contact_info,
        
        -- Media information
        sender_id,
        has_media,
        media_type,
        image_path,
        
        -- Metadata
        scraped_at,
        
        -- Parse JSON raw data safely
        case 
            when raw_data is not null and raw_data != 'null'::jsonb
            then (raw_data->>'views')::int
            else null
        end as message_views,
        
        case 
            when raw_data is not null and raw_data != 'null'::jsonb
            then (raw_data->>'forwards')::int
            else null
        end as message_forwards,
        
        -- Quality flags
        case 
            when message_text is null or trim(message_text) = '' 
            then true 
            else false 
        end as is_empty_message,
        
        case 
            when message_date > current_timestamp 
            then true 
            else false 
        end as is_future_date,
        
        -- Create business date (Ethiopian timezone approximation)
        (message_date + interval '3 hours')::date as business_date
        
    from source_data
),

final as (
    select 
        *,
        -- Create a unique business key
        md5(channel_name || '::' || message_id::text) as message_business_key,
        
        -- Add row quality score
        case 
            when is_empty_message then 0
            when is_future_date then 0
            when message_length < 10 then 1
            when not contains_medical_keywords and not has_media then 2
            else 3
        end as data_quality_score
        
    from cleaned_data
)

select * from final
