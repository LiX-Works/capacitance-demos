# Official deployment references

Checked against official GitHub documentation when preparing this package, 2026-10-02.

- Custom workflow and Pages action permissions: https://docs.github.com/en/pages/getting-started-with-github-pages/using-custom-workflows-with-github-pages
- Configure GitHub Actions or branch publication: https://docs.github.com/en/pages/getting-started-with-github-pages/configuring-a-publishing-source-for-your-github-pages-site
- Entry point / static-site limitations: https://docs.github.com/en/enterprise-cloud@latest/pages/getting-started-with-github-pages/creating-a-github-pages-site
- Node setup action: https://github.com/actions/setup-node
- Git file size limits: https://docs.github.com/en/repositories/working-with-files/managing-large-files/about-large-files-on-github

The provided workflow uses checkout v6, setup-node v7 with Node 22, configure-pages v5, upload-pages-artifact v4 and deploy-pages v4. It requires repository Pages configuration and account authorization; local validation does not prove an actual GitHub deployment succeeded.

The full ZIP is a handoff/backup container, not a file to commit in place of its contents. GitHub's documented regular-Git single-file ceiling is 100 MiB (warning above 50 MiB; browser-upload ceiling 25 MiB). The package audit lists the largest unpacked file. Do not use Git LFS pointers as a substitute for a Pages runtime asset.
