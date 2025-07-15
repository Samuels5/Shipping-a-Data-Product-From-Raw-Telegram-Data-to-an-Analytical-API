-- Fact table for image detections, linked to messages

{{ config(materialized='table') }}

with detections as (
    select 
        id as detection_id,
        channel_name,
        date as detection_date,
        image_path,
        detected_object_class,
        confidence_score,
        bbox_xmin,
        bbox_ymin,
        bbox_xmax,
        bbox_ymax,
        detected_at
    from {{ source('raw', 'image_detections') }}
),

message_lookup as (
    select 
        telegram_message_key,
        channel_name,
        message_date,
        image_path
    from {{ ref('stg_telegram_messages') }}
    where has_media and image_path is not null
),

joined as (
    select 
        d.detection_id,
        d.channel_name,
        d.detection_date,
        d.image_path,
        d.detected_object_class,
        d.confidence_score,
        d.bbox_xmin,
        d.bbox_ymin,
        d.bbox_xmax,
        d.bbox_ymax,
        d.detected_at,
        m.telegram_message_key,
        m.message_date
    from detections d
    left join message_lookup m
      on d.channel_name = m.channel_name
     and d.image_path = m.image_path
),

final as (
    select 
        -- Surrogate key
        {{ dbt_utils.generate_surrogate_key(['detection_id']) }} as image_detection_key,
        telegram_message_key,
        channel_name,
        detection_date,
        image_path,
        detected_object_class,
        confidence_score,
        bbox_xmin,
        bbox_ymin,
        bbox_xmax,
        bbox_ymax,
        detected_at,
        message_date,
        current_timestamp as created_at
    from joined
)

select * from final
