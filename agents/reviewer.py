import os, subprocess, shutil, json
from typing import Dict, Any
from github import Github

class ReviewerAgent:
    def __init__(self, repo=None, gh=None, auto_approve_env=False):
        self.repo = repo
        self.gh = gh
        self.auto_approve_env = auto_approve_env

    def run_cmd(self, cmd):
        try:
            p = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, check=False)
            return {'returncode': p.returncode, 'stdout': p.stdout, 'stderr': p.stderr}
        except Exception as e:
            return {'returncode':99,'stdout':'','stderr':str(e)}

    def lint_and_test(self):
        report = {}
        if shutil.which('ruff'):
            report['ruff'] = self.run_cmd(['ruff','--quiet','.'])
        else:
            report['ruff'] = {'skipped':True,'reason':'ruff not installed'}
        if shutil.which('bandit'):
            report['bandit'] = self.run_cmd(['bandit','-r','.'])
        else:
            report['bandit'] = {'skipped':True,'reason':'bandit not installed'}
        if shutil.which('pytest'):
            report['pytest'] = self.run_cmd(['pytest','-q'])
        else:
            report['pytest'] = {'skipped':True,'reason':'pytest not installed'}
        return report

    def evaluate(self, report):
        approved = True
        notes = []
        for k,v in report.items():
            if isinstance(v, dict) and v.get('returncode') not in (0,None,True):
                if v.get('returncode') != 0:
                    approved = False
                    notes.append(f"{k} failed")
        return approved, notes

    def post_review(self, pr_number, body, event='REQUEST_CHANGES', comments=None):
        if not self.repo:
            return False
        pr = self.repo.get_pull(pr_number)
        self.repo.get_pull(pr_number).create_review(body=body, event=event, comments=comments or [])
        return True

    def review_pr(self, pr_number):
        report = self.lint_and_test()
        approved, notes = self.evaluate(report)
        if approved:
            # Post approval
            self.post_review(pr_number, 'Automated review — approved', event='APPROVE')
            # Optionally add label 'approved'
            try:
                pr = self.repo.get_pull(pr_number)
                pr.add_to_labels('approved')
            except Exception:
                pass
            # Optionally auto-merge is handled in separate workflow
            return {'pr':pr_number,'approved':True,'notes':notes,'report':report}
        else:
            msg = 'Automated review found issues:\n' + '\n'.join(notes)
            self.post_review(pr_number, msg, event='REQUEST_CHANGES', comments=[])
            return {'pr':pr_number,'approved':False,'notes':notes,'report':report}
