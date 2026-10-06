"""Concise human and structured machine update reports."""


def human(report):
    if report.get('spatial_authority'):
        return '\n'.join(['Knowledge Atlas Update',report['status'],report.get('message',''),
            'Spatial authority: global-canonical-pyramid',
            'Generation: '+str(report['generation'])+' · Activation history: '+str(report['history_version']),
            'Existing displacement: 0 px · placement search: none', 'Applied: '+str(report['applied'])])
    if 'manifest' in report:
        m=report['manifest'];v=report.get('metrics',{});b=m['bindings']
        if m.get('selected_variant')=='CANONICAL_REVEAL':
            return '\n'.join(['Knowledge Atlas Canonical Reveal Preview', 'Outcome: '+m['outcome'],
                'New Categories: '+str(m['new_categories']), 'New Topics: '+str(m['new_topics']),
                'Existing displacement: 0 px · no placement search', 'Generation change: 0',
                'Activation history change: '+str(m['expected_history_change']),
                'Manifest fingerprint: '+m['manifest_fingerprint']])
        return '\n'.join(['Knowledge Atlas Activation Preview','Context: '+str(m['context']),
            'New Categories: '+str(m['new_categories']),'New Topics: '+str(m['new_topics']),
            'Blocked references: '+str(m['blocked_references']),'Selected variant: '+m['selected_variant'],
            'Existing nodes moved: '+str(v.get('existing_nodes_moved')),
            'Canvas growth: '+str(v.get('width_growth'))+' / '+str(v.get('height_growth')),
            'Overlaps / crossings: '+str(v.get('overlaps'))+' / '+str(v.get('hierarchy_crossings')),
            'Maximum parent drift: '+str(v.get('parent_centering_drift')),
            'Expected Generation change: '+str(m['expected_generation_change']),
            'Plan fingerprint: '+b['plan'],'Candidate fingerprint: '+b['candidate'],
            'Existing geometry fingerprint: '+b['existing_geometry']['geometry'],
            'Manifest fingerprint: '+m['manifest_fingerprint'],'Outcome: '+m['outcome']])
    if 'diff' not in report or 'presentation' not in report:
        return 'Knowledge Atlas Update\n' + report['status'] + '\n' + report.get('message', '')
    d, p = report['diff'], report['presentation']
    lines = ['Knowledge Atlas Update', '', 'Data changes', '------------',
             'Change types: ' + ', '.join(d['change_types'])]
    for row in d['projects']['state_transitions']:
        lines.append(f"Project {row['id']}: {row['before']} → {row['after']}")
    lines += [f"+{len(d['topics']['learned_added'])} learned topics", f"+{len(d['topics']['verified_added'])} verified topics",
              f"{len(d['topics']['added'])} new topics", f"{len(d['categories']['added'])} new categories",
              f"{len(d['relations']['pairs_added'])} new relation pairs", '', 'Presentation', '------------',
              f"Category displacement: {p['category_displacement']['max']:.3f}",
              f"Topic displacement: {p['topic_displacement']['max']:.3f}",
              f"Topic tray repacks: {len(p['repacked_topic_trays'])}",
              'Checkpoint changed: ' + ('yes' if p['checkpoint_changed'] else 'no'),
              f"Persisted generation: {p['persisted_generation']} · Candidate: {p['candidate_generation']}", '', 'Evidence', '--------',
              f"Project requirement records updated: {report['evidence']['requirements_updated']}",
              f"Topic evidence links added: {report['evidence']['links_added']}", '', 'Validation', '----------',
              'PASS', '', 'Affected Region', '---------------',
              'Origin: ' + (', '.join(report['region_impact']['origin_titles']) or 'none'),
              'Expected regions: ' + (', '.join(report['region_impact']['expected_regions']) or 'none'),
              'Moved categories: ' + (', '.join(r['title']+': '+str(r['displacement']) for r in report['region_impact']['moved_categories']) or 'none'),
              'Moved unrelated categories: ' + (', '.join(r['title'] for r in report['region_impact']['unrelated_moved_categories']) or 'none'),
              'Repacked trays: ' + (', '.join(report['region_impact']['repacked_trays']) or 'none'),
              'Escalation level: ' + str(report['region_impact']['escalation_level']),
              'Outcome: '+report['outcome'],
              'Applied: '+('yes' if report['applied'] else 'no'),
              'Safe to build preview: '+('YES' if report['safe_to_build_preview'] else 'NO'),
              'Mode: ' + report['mode']]
    if report.get('global_catalog', {}).get('observation_count'):
        catalog = report['global_catalog']
        lines += ['', 'Global catalog (data only)', '--------------------------',
                  f"{catalog['categories']} categories; {catalog['described_topics']} described Topics; {catalog['unresolved_references']} unresolved references",
                  'Global change types: ' + ', '.join(catalog['change_types']),
                  'Active projection changed: ' + ('yes' if catalog['active_projection_changed'] else 'no'),
                  'Geometry activation: no']
    if report.get('production'):
        production = report['production']
        lines += ['', 'Production', '----------', 'Target: ' + production['target'],
                  'Publication: ' + ('APPLIED' if report['applied'] else 'NOT APPLIED'),
                  'Browser regression: ' + ((production.get('validation') or {}).get('status', 'BLOCKED'))]
    return '\n'.join(lines)
