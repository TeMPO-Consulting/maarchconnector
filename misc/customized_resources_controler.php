<?php

class resources_controler
{
    // (...)
    /******* ALREADY EXISTING CODE *******/
    // (...)
    
    /*******************************************/
    /***** CUSTOMIZED WEBSERVICE *****/

    // add on top of page:
    //require_once 'core/class/class_db_pdo.php';
    
    /**
     * Research by subject, min. date, and optionnally category and contact name
     * Returns a list of documents
     */
    public function searchDocuments($searchDocumentsParams)
    {
        $db = new Database();
        
        // LEFT JOIN: the doc may not have been linked to a sender or addressee yet
        // COALESCE: if the category_id IS NULL replace it with an empty string
        $sql = "SELECT r.res_id, r.subject, r.doc_date, m.category_id as category, "
                . "m.exp_contact_id, m.dest_contact_id, m.exp_user_id, "
                . "m.dest_user_id "
                . "FROM res_letterbox as r "
                . "LEFT JOIN mlb_coll_ext as m ON r.res_id = m.res_id "
                . "WHERE UPPER(r.subject) LIKE UPPER(:subject) AND "
                . "r.doc_date >= to_date(:mindocdate, 'YYYY-MM-DD') "
                . "AND COALESCE(m.category_id, '') like :category "
                . "ORDER BY r.doc_date ASC;";
        
	/*********************
	Note : in the version 1.5.1 the following lines must be adapted:
	the "query" method has been modified and the "bind" method has been deleted
	*********************/
        $db->query($sql);  // prepared request
        $db->bind(":subject", "%$searchDocumentsParams->subject%");
        // the date is managed as a string
        $db->bind(':mindocdate', $searchDocumentsParams->min_doc_date);
        if(isset($searchDocumentsParams->category) &&
            !is_null($searchDocumentsParams->category) &&
            $searchDocumentsParams->category != "")
        {
            $db->bind(":category", $searchDocumentsParams->category);
        }
        else
        {
            // match all the categories (even NULL)
            $db->bind(":category", "%");
        }
        
        $res = $db->resultset(); // array of objects OR null
        
        // add the information about the contact (sender or addressee)
        $final_res = array();
        foreach ($res as $current)
        {
            if(!is_null($current['exp_contact_id']) || !is_null($current['dest_contact_id']))
            {
                $this->get_external_contact($db, $current);
            }
            else if(!is_null($current['exp_user_id']) || !is_null($current['dest_user_id']))
            {
                $this->get_internal_contact($db, $current);
            }
            else
            {
                $current['contact'] = '';
            }
            
            // remove the unused data
            unset($current['exp_contact_id']);
            unset($current['dest_contact_id']);
            unset($current['exp_user_id']);
            unset($current['dest_user_id']);
            
            array_push($final_res, $current);
        }
        
        // if the user wants to search by contact name we filter the data
        return $this->filter_by_contact($final_res, $searchDocumentsParams->contact);
    }
    
    /**
     * Get the firstname and lastname from the internal contact linked to the doc in parameter
     */
    private function get_internal_contact($db, &$doc)
    {
        $sql = "SELECT CONCAT(firstname, ' ', lastname) AS contact "
                . "FROM users "
                . "WHERE user_id = :user_id;";
        $db->query($sql);
        
        if(!is_null($doc['exp_user_id']))
        {
            $db->bind(":user_id", $doc['exp_user_id']);
        }
        else
        {
            $db->bind(":user_id", $doc['dest_user_id']);
        }
        
        $res = $db->single();
        $doc['contact'] = $res['contact'];
    }
    
    /**
     * Get the contact details from the external contact linked to the doc in parameter
     * 
     * Get the firstname and lastname if it's a private individual or the complete
     * name and possibly shortname if it's a society
     */
    private function get_external_contact($db, &$doc)
    {
        $sql = "SELECT is_corporate_person, society, society_short, firstname, lastname "
                . "FROM contacts_v2 "
                . "WHERE contact_id = :contact_id;";
        
        $db->query($sql);
        
        if(!is_null($doc['exp_contact_id']))
        {
            $db->bind(":contact_id", $doc['exp_contact_id']);
        }
        else
        {
            $db->bind(":contact_id", $doc['dest_contact_id']);
        }
        
        $res = $db->single();
        
        $contact = '';
        if($res['is_corporate_person'] == 'Y')
        {
            // it's a society
            $contact .= $res['society'];
            if(!is_null($res['society_short']) && !empty($res['society_short']))
            {
                $contact .= " (" . $res['society_short'] . ")";
            }
        }
        else
        {
            // it's a private individual
            $contact .= $res['firstname'] . " " . $res['lastname'];
        }
        
        $doc['contact'] = $contact;
    }
    
    /**
     * Get only the documents from the list that are linked to the contact in parameter
     */
    private function filter_by_contact($list, $contact)
    {
        $res = array();
        
        if(isset($contact) && !is_null($contact) && $contact != "")
        {
            foreach ($list as $elem)
            {
                // case insensitive research
                if(stristr($elem['contact'], $contact))
                {
                    array_push($res, $elem);
                }
            }
            
            return $res;
        }
        else
        {
            return $list;
        }
    }
}
