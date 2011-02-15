/*
#########################################################
## Copyright 2008 The Trustees of Indiana University
##
## Licensed under the Apache License, Version 2.0 (the "License");
## you may not use this file except in compliance with the License.
## You may obtain a copy of the License at
##
##      http://www.apache.org/licenses/LICENSE-2.0
##
## Unless required by applicable law or agreed to in writing, software
## distributed under the License is distributed on an "AS IS" BASIS,
## WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
## See the License for the specific language governing permissions and
## limitations under the License.
#########################################################

    Usage: mysql <manageBOV.sql
*/
use microbial;

delete from BOV_project,BOV_result,BOV_hit,BOV_hsp using BOV_hsp inner join BOV_hit inner join BOV_result inner join BOV_project where DATEDIFF(NOW(),BOV_project.created_on)>_____LIFETIME_____ and  BOV_project.id=BOV_result.project_id and BOV_result.id=BOV_hit.result_id and  BOV_hit.id=BOV_hsp.hit_id;

