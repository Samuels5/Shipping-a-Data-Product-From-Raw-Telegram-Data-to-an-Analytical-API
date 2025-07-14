-- Test that ensures all channels have reasonable message counts
-- No channel should have 0 messages if it exists in the fact table

select 
    channel_name,
    total_messages
from {{ ref('dim_channels') }}
where total_messages = 0
