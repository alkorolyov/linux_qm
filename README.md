# linux_orca
Installation of orca in Linux

1) Download from ORCA 5.0.3 version from forum and save it to the `/tmp`

   `https://orcaforum.kofo.mpg.de/app.php/dlext/?view=detail&df_id=180`

2) download `install.sh` and `orcainit` from this repository in the user home folder
   
   ```
   sudo bash install.sh
   echo "source ~/orcainit" >> ~/.bashrc
   ```

3) Test the installation

   `orca test.orca --use-hwthread-cpus`
