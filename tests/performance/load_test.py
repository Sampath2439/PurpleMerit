# load_test.py
import asyncio
import aiohttp
import time

async def test_lead_processing():
    """Test lead triage under load"""
    async with aiohttp.ClientSession() as session:
        tasks = []
        for i in range(100):
            task = session.post(
                'https://api.marketing-system.internal/api/v1/leads/test-123/triage',
                json={'priority': 'medium'}
            )
            tasks.append(task)
        
        start_time = time.time()
        responses = await asyncio.gather(*tasks, return_exceptions=True)
        end_time = time.time()
        
        success_count = sum(1 for r in responses if hasattr(r, 'status') and r.status == 200)
        print(f"Processed {success_count}/100 requests in {end_time - start_time:.2f}s")

if __name__ == "__main__":
    asyncio.run(test_lead_processing())