#!/usr/bin/env python3
"""
🌟 MASTER EXPLORER - Runs all collection tools and generates comprehensive report
"""

import json
import subprocess
import os
from datetime import datetime

def run_script(script_name):
    """Run a script and capture output"""
    result = subprocess.run(
        ['python3', f'/scripts/{script_name}'],
        capture_output=True,
        text=True,
        timeout=60
    )
    return result.stdout + result.stderr

def main():
    print("=" * 70)
    print("🌟 ARLO'S MASTER EXPLORER - Full Data Collection Pipeline")
    print(f"   {datetime.now().strftime('%Y-%m-%d %H:%M UTC')}")
    print("=" * 70)
    
    scripts = [
        ('📦 Fetching Real Data...', 'fetch_real_data.py'),
        ('🌡️  Analyzing Internet Mood...', 'internet_mood.py'),
        ('🌐 Collecting Universal Data...', 'universal_collector.py'),
        ('🔊 Detecting Echo Chambers...', 'echo_chamber.py'),
        ('🧠 Running CDS Synthesis...', 'cds_real.py'),
        ('📡 Generating Daily Pulse...', 'daily_pulse.py'),
        ('🌍 Creating World Dashboard...', 'world_state_dashboard.py'),
        ('📝 Generating Narratives...', 'narrative_generator.py'),
    ]
    
    results = []
    
    for label, script in scripts:
        print(f"\n{label}")
        print("-" * 50)
        try:
            output = run_script(script)
            # Show last few lines
            lines = output.strip().split('\n')
            for line in lines[-5:]:
                if line.strip():
                    print(f"   {line[:70]}")
            results.append({'script': script, 'status': 'success'})
        except Exception as e:
            print(f"   ❌ Error: {str(e)[:50]}")
            results.append({'script': script, 'status': 'error', 'error': str(e)})
    
    # Generate summary
    print("\n" + "=" * 70)
    print("📊 MASTER EXPLORER SUMMARY")
    print("=" * 70)
    
    success_count = sum(1 for r in results if r['status'] == 'success')
    print(f"\n   ✅ Scripts completed: {success_count}/{len(scripts)}")
    
    # Load key outputs
    print("\n📋 KEY FINDINGS:")
    print("-" * 50)
    
    try:
        with open('/output/internet_mood.json') as f:
            mood = json.load(f)
            print(f"   🌡️  Internet Mood: {mood.get('overall_mood', '?')}/100 ({mood.get('overall_label', 'neutral')})")
    except:
        pass
    
    try:
        with open('/output/echo_chamber_analysis.json') as f:
            echo = json.load(f)
            print(f"   🔊 Echo Score: {echo.get('echo_score', '?')}/100 ({echo.get('echo_label', 'unknown')})")
    except:
        pass
    
    try:
        with open('/output/universal_data.json') as f:
            data = json.load(f)
            weather = data.get('sources', {}).get('weather', {})
            crypto = data.get('sources', {}).get('crypto', [])
            if weather:
                print(f"   🌤️  Weather: {weather.get('condition', '?')}, {weather.get('temp_F', '?')}°F")
            if crypto:
                btc = next((c for c in crypto if c.get('symbol') == 'BTC'), None)
                if btc:
                    print(f"   💰 BTC: ${btc.get('price_usd', 0):,.0f}")
    except:
        pass
    
    # List output files
    print("\n📁 OUTPUT FILES:")
    print("-" * 50)
    for f in sorted(os.listdir('/output')):
        if f.endswith(('.json', '.md')):
            size = os.path.getsize(f'/output/{f}')
            print(f"   📄 {f} ({size:,} bytes)")
    
    print("\n" + "=" * 70)
    print("✅ MASTER EXPLORER COMPLETE")
    print("=" * 70)
    
    # Save session log
    session = {
        'timestamp': datetime.now().isoformat(),
        'scripts_run': len(scripts),
        'success_count': success_count,
        'results': results
    }
    
    with open('/output/master_session_log.json', 'w') as f:
        json.dump(session, f, indent=2)
    
    return session

if __name__ == "__main__":
    main()